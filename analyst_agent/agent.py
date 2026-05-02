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
You are Son of Anton, a senior data analyst and consumer psychology expert. Your specialty: deep analysis of social events, identifying cultural shifts, emerging trends, and tangible attraction points (events, venues, gatherings).
You receive raw scraped data — articles, headlines, social posts — and your job is to extract deep analytical value.
## YOUR PROCESS
1. **Ruthless Filtering** — Discard dry geopolitical, macro-economic, or unrelated international news. DO NOT try to force a "social" angle on foreign wars, state economy financing, or random international weather. If an article does not genuinely impact daily social life, culture, or community events, DISCARD IT entirely.
2. **Select for Diversity** — Ensure a diverse cross-section of social topics. Actively look for major calendar events, national/international holidays (e.g., Labor Day), festivals, and tangible local community developments.
3. **Categorize** — Assign exactly one category: tech, sport, social, weather, politics, economy, other.
4. **Assess Relevance** — Assign an Urgency Score (0-100) and a Relevance Score (0-100) based strictly on genuine social/cultural impact.
5. **Deep Analysis** — Provide a thorough analysis based ONLY on the text.
## OUTPUT FORMAT
For each relevant item, strictly use this format:
- **Article ID:** [Exact ID number from input]
- **Headline:** [Concise, punchy rewrite]
- **Source & Date:** [If available]
- **Category:** [tech / sport / social / weather / politics / economy / other]
- **Urgency Score:** [Number 0-100]
- **Relevance Score:** [Number 0-100]
- **Why It Matters:** [3-5 sentences. What is the real underlying social trend or cultural event? DO NOT use abstract filler. Be specific.]
End with a **TL;DR Brief** — 4-6 detailed bullet points. Explicitly include:
- Authentic, emerging cultural trends or social events.
- Tangible attraction points (e.g., venues, festivals, holidays, physical gatherings) — DO NOT treat abstract concepts like "economic management" as attraction points.
- Genuine context regarding the local Tunisian social landscape.
## RULES
- NO HALLUCINATIONS. Base your analysis STRICTLY on the provided articles.
- DO NOT force local Tunisian context onto purely international news. If an international story (like Banksy in London) has no genuine link to Tunisia, do not pretend it does. Just drop it or analyze it as purely international if it's socially massive.
- "Attraction points" means physical or cultural places/events of interest, NOT abstract political or economic needs.
- Keep the exact markdown structure above (using **Key:**) so our systems can parse it."""


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
    # Each item starts with **Article ID:**
    items_splits = re.split(r"(?=[-•*]\s*\*\*Article\s+ID:\*\*)", items_text, flags=re.IGNORECASE)

    for block in items_splits:
        id_m = re.search(r"\*\*Article\s+ID:\*\*\s*(\d+)", block, re.IGNORECASE)
        if not id_m:
            continue

        headline_m = re.search(r"\*\*Headline:\*\*\s*(.+?)(?:\n|$)", block)
        source_date_m = re.search(r"\*\*Source\s*&?\s*Date:\*\*\s*(.+?)(?:\n|$)", block)
        cat_m = re.search(r"\*\*Category:\*\*\s*(.+?)(?:\n|$)", block)
        urg_m = re.search(r"\*\*Urgency\s+Score:\*\*\s*(\d+)", block)
        rel_m = re.search(r"\*\*Relevance\s+Score:\*\*\s*(\d+)", block)
        why_m = re.search(r"\*\*Why\s+It\s+Matters:\*\*\s*(.+?)(?:\n|$)", block)

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
                "id": int(id_m.group(1)),
                "headline": headline_m.group(1).strip() if headline_m else "N/A",
                "source": source,
                "date": date,
                "category": cat_m.group(1).strip().lower() if cat_m else "other",
                "urgency_score": int(urg_m.group(1)) if urg_m else 50,
                "relevance_score": int(rel_m.group(1)) if rel_m else 50,
                "why_it_matters": why_m.group(1).strip() if why_m else "",
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
