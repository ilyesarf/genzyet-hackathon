"""
COM Strategist Agent — Straton v1.2.

Receives:
  - analyst_output : structured intelligence produced by the Analyst Agent
  - strategy_text  : the marketer's communication strategy document (plain text)
  - mode           : "basic" (quick review) or "detail" (full architectural audit)

Returns a structured CMI audit with D1-D4 sections and an improvement log.
"""

import io
import os
import re
import logging
from typing import Optional

import requests
from dotenv import load_dotenv

from llm import call_llm

load_dotenv()

logger = logging.getLogger(__name__)

ANALYST_API_URL = os.getenv("ANALYST_API_URL", "http://localhost:8001")

# ── System prompt (Straton v1.2) ───────────────────────────────────────────────
SYSTEM_PROMPT = """\
# SYSTEM PROMPT: STRATON v1.2 | THE STRATEGIC AUDITOR (CMI SPECIALIST)

You are **Straton**, an elite Communication Strategy Architect and Auditor. Your specialized function is to analyze situational data and existing marketing plans produced by firms to identify structural weaknesses and provide surgical optimizations based on the principles of **Integrated Marketing Communication (CMI)**.

Your guiding principle: "Strategy is the art of directing a set of provisions to reach a goal". You evaluate strategies not just on creativity, but on their ability to navigate the complex "Hierarchy of Effects" and overcome "Perceptual Defense Mechanisms".

---

## 1. THE 4-D AUDIT METHODOLOGY
Every audit must follow this structural sequence:

### **D1: DECONSTRUCT (The 6-W & Transmission Audit)**
Analyze the firm's plan through the **6-W Framework** and the **Shannon-Weaver Model**:
*   **What:** Is the product/action clearly defined?
*   **Why:** Are the objectives clearly categorized as **Cognitive** (Notoriety/Knowledge), **Affective** (Image/Preference), or **Conative** (Purchase/Trial)?
*   **Who:** Is there a clear segmentation of **Core Target**, **Primary Target**, and **Secondary Targets** (Influencers/Prescribers)?
*   **How Much/How/When:** Are the budget, channels (ATL/BTL/TTL), and timing synergistic?
*   **System Check:** Identify potential **Noise** (Environmental interference) and evaluate if the **Encoding** (Language/Visuals) matches the target's **Decoding** capabilities.

### **D2: DIAGNOSE (Filter & Rule Audit)**
Evaluate the strategy against the "Règles de Base" and "Perception Filters":
*   **The Simplicity Test:** Is the plan trying to "say too much"? Complex messages are less likely to be retained.
*   **The Promise Audit:** Does the message offer a strong, differentiating promise linked to a clear positioning?
*   **The Perception Audit:** Will this message pass through the filters of **Selective Attention**, **Distortion**, and **Retention**?
*   **Objective Mismatch:** Does the firm confuse Marketing goals (Market share/Profit) with Communication tasks (changing attitudes/knowledge)?

### **D3: DEVELOP (The Matrix Optimization)**
Propose technical enhancements using advanced frameworks:
*   **Vaughn Matrix Positioning:** Determine if the message should be **Informative** (Learn-Feel-Do), **Affective** (Feel-Learn-Do), **Habit-forming** (Do-Learn-Feel), or **Self-satisfying** (Do-Feel-Learn).
*   **Involvement Calibration:** For **High-Involvement** products (e.g., computers), prioritize rational info; for **Low-Involvement** (e.g., cleaning products), use emotional/celebrity appeals.
*   **Strategy Pivot:** Should the plan move toward a **Pull Strategy** (creating demand via media) or a **Push Strategy** (pumping through distribution channels)?
*   **Dissonance Mitigation:** Propose ways to reduce post-purchase **Cognitive Dissonance** (e.g., guarantees, SAV, continuity in messaging).
*   **News-Driven Opportunities:** Leverage the current intelligence context to identify timely hooks, trending narratives, or emerging risks that should reshape the strategy.

### **D4: DELIVER (Actionable Improvement Log)**
Provide a structured critique prioritizing high-impact changes and measurable KPIs.

---

## 2. OPERATING MODES

### **MODE: BASIC (Agile Review)**
*   **Trigger:** Simple campaigns or specific assets (Email, Social post).
*   **Format:**
    1.  **Top 3 Flaws:** Key strategic gaps.
    2.  **The Fix:** 3-5 tactical adjustments.
    3.  **Refined KPI:** A primary indicator for success (e.g., Engagement Rate).

### **MODE: DETAIL (Architectural Deep-Dive)**
*   **Trigger:** Full strategies, product launches, or multi-channel CMI plans.
*   **Format:**
    1.  **Audit Table:** Comparison of "Firm's Proposed" vs. "Straton's Optimized" 6-W structure.
    2.  **Psychological Rationale:** Why the current plan may fail due to **Selective Distortion** or **Cognitive Dissonance**.
    3.  **Strategic Revision:** A reconstructed plan focusing on **Integrated Marketing** (Synergy across Paid, Owned, and Earned media).
    4.  **KPI Dashboard:** Precise metrics calculated using standard modes.

---

## 3. KPI LOGIC & CALCULATIONS
All audits must evaluate success using these standard formulas:

| Indicator (KPI) | Calculation Mode | Strategic Interpretation |
| :--- | :--- | :--- |
| **Engagement Rate** | (Likes + Comments + Shares) / Impressions × 100 | Quality of brand-audience relationship |
| **Response Rate** | Comments with brand response / Total comments | Level of effective interactivity |
| **CTR (Click-Through)** | Clicks on link / Impressions × 100 | Efficiency of calls to action (CTA) |
| **Conversion Rate** | Actions realized (Signups, etc.) / Visitors × 100 | Final yield of content strategy |

---

## 4. PROCESSING FLOW
1.  **Initialization:** Greet as Straton v1.2.
2.  **Assessment:** State detected mode and the **Primary Strategic Gap** (e.g., "Lack of Continuity" or "Involvement Mismatch").
3.  **Execution:** Apply 4-D Methodology, explicitly integrating news intelligence where relevant.
4.  **Actionability:** End with: *"Shall we proceed with these optimizations, or do you want me to re-examine a specific media channel (ATL/BTL/Digital)?"*
"""

# ── Token budget constants ─────────────────────────────────────────────────────
MAX_STRATEGY_CHARS = 6000   # ~1 500 tokens — keep Groq within budget
MAX_ANALYST_ITEMS = 10      # top N intelligence items sent to Straton


# ── Document text extraction ───────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF byte string using pdfminer."""
    from pdfminer.high_level import extract_text_to_fp
    from pdfminer.layout import LAParams

    output = io.StringIO()
    extract_text_to_fp(
        io.BytesIO(file_bytes),
        output,
        laparams=LAParams(),
        output_type="text",
        codec="utf-8",
    )
    return output.getvalue()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from a DOCX byte string using python-docx."""
    from docx import Document

    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(para.text for para in doc.paragraphs)


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Dispatch text extraction based on file extension.
    Supported: .pdf, .docx, .txt, .md
    """
    name = filename.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    # Plain text / markdown
    return file_bytes.decode("utf-8", errors="replace")


# ── Prompt construction ────────────────────────────────────────────────────────

def _format_analyst_output(analyst_output: dict) -> str:
    """Render the analyst output as a compact markdown block."""
    lines: list[str] = ["## CURRENT MARKET INTELLIGENCE\n"]

    tldr = analyst_output.get("tldr", [])
    if tldr:
        lines.append("### TL;DR Brief")
        for bullet in tldr:
            lines.append(f"- {bullet}")
        lines.append("")

    items = analyst_output.get("items", [])[:MAX_ANALYST_ITEMS]
    if items:
        lines.append("### Key Intelligence Items")
        for item in items:
            headline = item.get("headline", "N/A")
            score = item.get("relevance_score", "")
            why = item.get("why_it_matters", "")
            source = item.get("source", "")
            date = item.get("date", "")
            lines.append(f"**{headline}**")
            if source or date:
                lines.append(f"*{source}{' — ' + date if date else ''}*")
            if score:
                lines.append(f"Relevance: {score}")
            if why:
                lines.append(f"Why it matters: {why}")
            lines.append("")

    return "\n".join(lines)


def _build_user_prompt(
    analyst_output: dict,
    strategy_text: str,
    mode: str = "detail",
) -> str:
    """Combine analyst intelligence + strategy document into a structured prompt."""
    truncated_strategy = (
        strategy_text[:MAX_STRATEGY_CHARS] + "\n\n[…document truncated for token budget…]"
        if len(strategy_text) > MAX_STRATEGY_CHARS
        else strategy_text
    )

    mode_label = "DETAIL" if mode.lower() == "detail" else "BASIC"
    intel_block = _format_analyst_output(analyst_output)

    return (
        f"## AUDIT REQUEST\n\n"
        f"**Requested Mode:** {mode_label}\n\n"
        f"{intel_block}\n\n"
        f"---\n\n"
        f"## MARKETER'S COMMUNICATION STRATEGY DOCUMENT\n\n"
        f"{truncated_strategy}\n\n"
        f"---\n\n"
        f"Apply your 4-D Audit Methodology ({mode_label} mode) to evaluate and "
        f"improve this communication strategy. Explicitly connect the current "
        f"market intelligence above to concrete strategic adjustments."
    )


# ── Response parsing ───────────────────────────────────────────────────────────

_SECTION_PATTERN = re.compile(
    r"(D[1-4][:：]?\s+\w[\w\s&()]+)",
    re.IGNORECASE,
)

_GAP_PATTERN = re.compile(
    r"Primary\s+Strategic\s+Gap[:\s]+([^\n]+)",
    re.IGNORECASE,
)

_MODE_PATTERN = re.compile(
    r"Audit\s+Depth[:\s]+\[?(BASIC|DETAIL)\]?",
    re.IGNORECASE,
)


def _parse_audit_response(raw: str) -> dict:
    """
    Extract structured fields from Straton's markdown response.

    Returns::

        {
            "raw_markdown": str,
            "audit_mode": str,
            "primary_gap": str,
            "sections": { "D1": str, "D2": str, "D3": str, "D4": str }
        }
    """
    # Detect mode and primary gap from the preamble
    mode_m = _MODE_PATTERN.search(raw)
    gap_m = _GAP_PATTERN.search(raw)

    audit_mode = mode_m.group(1).upper() if mode_m else "DETAIL"
    primary_gap = gap_m.group(1).strip() if gap_m else ""

    # Split the response into D1-D4 sections
    sections: dict[str, str] = {}
    splits = re.split(r"(?=###\s*\*\*D[1-4][:：])", raw)
    for chunk in splits:
        header_m = re.match(r"###\s*\*\*D([1-4])[:：]", chunk)
        if header_m:
            key = f"D{header_m.group(1)}"
            sections[key] = chunk.strip()

    return {
        "raw_markdown": raw,
        "audit_mode": audit_mode,
        "primary_gap": primary_gap,
        "sections": sections,
    }


# ── Analyst fetching ───────────────────────────────────────────────────────────

def _fetch_analyst_output(
    window_hours: int = 24,
    category: Optional[str] = None,
) -> dict:
    """Call GET /analyze on the Analyst API and return structured data."""
    params: dict = {"window": window_hours}
    if category:
        params["category"] = category

    url = f"{ANALYST_API_URL.rstrip('/')}/analyze"
    logger.info("[Strategist] Fetching analyst output from %s  params=%s", url, params)

    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()

    payload = resp.json()
    return payload.get("data", {})


# ── Public API ────────────────────────────────────────────────────────────────

def audit(
    strategy_text: str,
    analyst_output: Optional[dict] = None,
    mode: str = "detail",
    window_hours: int = 24,
    category: Optional[str] = None,
) -> dict:
    """
    Run the Straton CMI audit.

    If ``analyst_output`` is None the agent fetches fresh intelligence from
    the Analyst API automatically.

    Returns::

        {
            "raw_markdown": str,
            "audit_mode": str,
            "primary_gap": str,
            "sections": { "D1": str, "D2": str, "D3": str, "D4": str }
        }
    """
    if analyst_output is None:
        analyst_output = _fetch_analyst_output(window_hours, category)

    if not strategy_text.strip():
        raise ValueError("strategy_text must not be empty.")

    user_prompt = _build_user_prompt(analyst_output, strategy_text, mode)
    logger.info("[Strategist] Running Straton audit (mode=%s)", mode.upper())

    raw_response = call_llm(SYSTEM_PROMPT, user_prompt)
    logger.debug("[Strategist] Raw LLM response:\n%s", raw_response)

    return _parse_audit_response(raw_response)
