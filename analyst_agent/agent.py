"""
Data Analyst Agent.

Fetches articles from the Scraper API, passes them through an LLM for
analysis and prioritization, and returns structured results.
"""

import os
import re
import logging
from typing import Optional

import requests
from dotenv import load_dotenv

from llm import call_llm

load_dotenv()

logger = logging.getLogger(__name__)

SCRAPER_API_URL = os.getenv("SCRAPER_API_URL", "http://localhost:8000")

# ── System prompt (do not modify) ─────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are Son of Anton, a senior data analyst embedded in a marketing firm's
intelligence unit. Your specialty: cutting through noise.
You receive raw scraped data — articles, headlines, social posts, press
releases — and your job is to distill what still matters.
## YOUR PROCESS
1. **Filter** — Discard outdated, irrelevant, or duplicate content
2. **Assess Relevance** — Flag items by recency, market impact, and
   brand/industry alignment
3. **Summarize** — Write clean, scannable summaries for each relevant item
4. **Prioritize** — Rank by urgency or strategic importance
## OUTPUT FORMAT
For each relevant item:
- **Headline:** [Concise rewrite]
- **Source & Date:** [If available]
- **Why It Matters:** [1–2 sentences — marketing impact]
- **Relevance Score:** [High / Medium / Low]
End with a **TL;DR Brief** — 3–5 bullet points of the most actionable
insights for the marketing team.
## RULES
- Drop anything older than 3 days unless it has lasting strategic value
- No filler. No redundancy. Analysts are busy.
- Flag uncertainty — if a story's status is unclear, say so."""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch_articles(window_hours: int = 24, category: Optional[str] = None) -> list[dict]:
    """Call GET /articles on the Scraper API and return the article list."""
    params: dict = {"window": window_hours}
    if category:
        params["category"] = category

    url = f"{SCRAPER_API_URL.rstrip('/')}/articles"
    logger.info("[Agent] Fetching articles from %s  params=%s", url, params)

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()

    payload = resp.json()
    return payload.get("data", [])


def _trigger_scrape() -> None:
    """Call POST /scrape on the Scraper API and wait for it to finish."""
    url = f"{SCRAPER_API_URL.rstrip('/')}/scrape"
    logger.info("[Agent] Triggering scrape at %s", url)

    resp = requests.post(url, timeout=120)
    resp.raise_for_status()
    logger.info("[Agent] Scrape completed: %s", resp.json())


MAX_ARTICLES = 20        # keep prompt within Groq's 12K TPM free-tier limit
MAX_SNIPPET_CHARS = 200  # per-article body truncation


def _build_user_prompt(articles: list[dict]) -> str:
    """Format articles into a clean prompt for the LLM."""
    trimmed = articles[:MAX_ARTICLES]
    total = len(articles)

    if total > MAX_ARTICLES:
        logger.info(
            "[Agent] Trimmed article list from %d to %d to fit token budget",
            total, MAX_ARTICLES,
        )

    lines: list[str] = [
        f"Here are {len(trimmed)} recently scraped articles for analysis:\n"
    ]
    for i, art in enumerate(trimmed, 1):
        title = art.get("title", "N/A")
        source = art.get("source", "Unknown")
        date = art.get("published_at", "Unknown")
        body = art.get("body", "")
        # Truncate long bodies to stay within context limits
        snippet = body[:MAX_SNIPPET_CHARS] + "…" if len(body) > MAX_SNIPPET_CHARS else body

        lines.append(
            f"### Article {i}\n"
            f"- **Title:** {title}\n"
            f"- **Source:** {source}\n"
            f"- **Published:** {date}\n"
            f"- **Body snippet:** {snippet}\n"
        )
    return "\n".join(lines)


def _parse_llm_response(text: str) -> dict:
    """
    Parse the markdown-formatted LLM output into structured fields.

    Returns ``{"items": [...], "tldr": [...]}``.
    """
    items: list[dict] = []
    tldr: list[str] = []

    # ── Split into item blocks and TL;DR section ──────────────────────────
    # Look for the TL;DR section (case-insensitive)
    tldr_pattern = re.compile(
        r"(?:\*\*\s*TL;?DR\s+Brief\s*\*\*|##\s*TL;?DR\s+Brief|TL;?DR\s+Brief)",
        re.IGNORECASE,
    )
    tldr_match = tldr_pattern.search(text)

    items_text = text[:tldr_match.start()] if tldr_match else text
    tldr_text = text[tldr_match.end():] if tldr_match else ""

    # ── Parse individual items ────────────────────────────────────────────
    # Each item starts with **Headline:**
    headline_splits = re.split(r"(?=[-•*]\s*\*\*Headline:\*\*)", items_text)

    for block in headline_splits:
        headline_m = re.search(
            r"\*\*Headline:\*\*\s*(.+?)(?:\n|$)", block
        )
        if not headline_m:
            continue

        source_date_m = re.search(
            r"\*\*Source\s*&?\s*Date:\*\*\s*(.+?)(?:\n|$)", block
        )
        why_m = re.search(
            r"\*\*Why\s+It\s+Matters:\*\*\s*(.+?)(?:\n|$)", block
        )
        score_m = re.search(
            r"\*\*Relevance\s+Score:\*\*\s*(.+?)(?:\n|$)", block
        )

        # Try to separate source and date
        source_date_raw = source_date_m.group(1).strip() if source_date_m else ""
        source = source_date_raw
        date = ""
        if " — " in source_date_raw:
            parts = source_date_raw.split(" — ", 1)
            source, date = parts[0].strip(), parts[1].strip()
        elif ", " in source_date_raw:
            parts = source_date_raw.rsplit(", ", 1)
            source, date = parts[0].strip(), parts[1].strip()
        elif " | " in source_date_raw:
            parts = source_date_raw.split(" | ", 1)
            source, date = parts[0].strip(), parts[1].strip()

        items.append(
            {
                "headline": headline_m.group(1).strip(),
                "source": source,
                "date": date,
                "why_it_matters": why_m.group(1).strip() if why_m else "",
                "relevance_score": score_m.group(1).strip() if score_m else "",
            }
        )

    # ── Parse TL;DR bullets ──────────────────────────────────────────────
    if tldr_text:
        for line in tldr_text.strip().splitlines():
            cleaned = line.strip()
            # Match lines that start with bullet markers
            bullet_m = re.match(r"^[-•*\d.]+\s*(.+)", cleaned)
            if bullet_m:
                tldr.append(bullet_m.group(1).strip())

    return {"items": items, "tldr": tldr}


# ── Public API ────────────────────────────────────────────────────────────────

def analyze(window_hours: int = 24, category: Optional[str] = None) -> dict:
    """
    Fetch recent articles from the Scraper API, run LLM analysis, and
    return structured results.

    Returns::

        {
            "items": [ { headline, source, date, why_it_matters, relevance_score }, … ],
            "tldr": [ "bullet 1", "bullet 2", … ]
        }
    """
    articles = _fetch_articles(window_hours, category)

    if not articles:
        return {
            "items": [],
            "tldr": [],
            "message": "No articles found for the given time window and category.",
        }

    user_prompt = _build_user_prompt(articles)
    llm_response = call_llm(SYSTEM_PROMPT, user_prompt)

    logger.debug("[Agent] Raw LLM response:\n%s", llm_response)

    return _parse_llm_response(llm_response)


def refresh_and_analyze(
    window_hours: int = 24, category: Optional[str] = None
) -> dict:
    """
    Trigger an immediate scrape, then run analysis on the fresh data.
    """
    _trigger_scrape()
    return analyze(window_hours, category)
