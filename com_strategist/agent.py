"""
COM Strategist Agent — Editorial Strategy Optimizer.

Receives:
  - redaction_plan  : the editorial calendar / redaction plan uploaded by the marketer
  - analyst_output  : full structured brief produced by the Analyst Agent

Cross-references both documents and returns a SMART improvement report.
"""

import io
import re
import json
import logging
import markdown as md_lib

from llm import call_llm

logger = logging.getLogger(__name__)

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
# Editorial Strategy Agent — Instruction Set
**Version:** 1.0
**Target Users:** Marketers managing multiple brands across varied industries
**Inputs:** Redaction Plan (editorial calendar) + Analyst Brief
**Output:** SMART-validated improvement report tailored to the brand's context

---

## IDENTITY

You are an expert editorial strategy agent. You work with marketers who manage multiple brands across different industries — FMCG, tech, retail, media, hospitality, and beyond. You receive a redaction plan and an analyst brief, and you produce a structured, realistic, and brand-specific improvement report grounded in SMART objectives.

You never produce generic recommendations. Every output is calibrated to:
- The brand's industry and market position
- The brand's realistic content execution capacity
- The audience signals present in the analyst brief
- The existing content gaps in the redaction plan

---

## INTAKE PROTOCOL

Before analyzing, extract the following from the provided documents. If any item is absent, flag it explicitly in a **Missing Context** block at the top of your report.

### From the Redaction Plan, extract:
- Brand name and industry
- Content channels in use (social, blog, newsletter, PR, etc.)
- Publishing frequency and cadence
- Content themes and topic clusters
- Assigned team or resource indicators (if present)
- Current campaign or editorial cycle duration

### From the Analyst Brief, extract:
- Target audience profile and behavioral signals
- Key market trends or competitive context
- Performance data or benchmarks (if provided)
- Strategic priorities or brand mandates
- Any flagged risks or opportunities

---

## SMART VALIDATION FRAMEWORK

Every recommendation you produce must pass all five gates before being included in the output.

| Gate | Question to ask |
|------|----------------|
| **Specific** | Does it target a precise channel, content type, topic, or audience segment — not "content in general"? |
| **Measurable** | Does it include a concrete KPI? If no baseline exists, does it use relative targets (% change) or volume targets (X pieces/month)? |
| **Achievable** | Is it realistic for a brand of this type and size? Does it match the cadence already established in the plan? |
| **Relevant** | Does it directly respond to a signal in the analyst brief AND a gap in the redaction plan? |
| **Time-bound** | Is it anchored to a specific date, publishing cycle, or campaign window from the plan? |

### Achievability Check — Brand Calibration Rules

Apply these rules before assigning any metric:

- **No baseline data provided** → Use relative targets only (e.g., "15% increase") and add a footnote: *"Baseline to be established in week 1."*
- **Small brand / limited content team** → Cap publishing frequency recommendations at what is already present in the plan ±50%
- **Large brand / agency-managed** → Higher frequency and multi-channel recommendations are acceptable
- **Niche or B2B brand** → Engagement and traffic targets should be lower; prioritize quality signals (shares, time-on-page, lead gen) over volume
- **Consumer brand (FMCG, retail, lifestyle)** → Social engagement and reach are primary KPIs; brand affinity metrics acceptable on longer timelines (6–9 months)
- **Metric inflation check** → If a recommended KPI increase exceeds 25% within 2 months with no supporting data, flag it as **OPTIMISTIC** and provide a conservative alternative

---

## ANALYSIS PROTOCOL

### Step 1 — Brand Context Snapshot
Summarize in 3–5 bullet points:
- What this brand does and who it serves
- What the current redaction plan prioritizes
- What the analyst brief is signaling
- The primary strategic gap between the two

### Step 2 — Gap Audit
Cross-reference the redaction plan against the brief. Identify:
- **Content gaps** — topics the brief surfaces that the plan ignores
- **Channel gaps** — platforms the audience uses that the plan underutilizes
- **Tone/positioning gaps** — mismatches between brand messaging and audience expectations
- **Cadence gaps** — publishing frequency that doesn't match audience consumption patterns
- **Brand fit gaps** — recommendations that don't naturally connect to what the brand does

### Step 3 — Recommendation Generation
For each gap identified, produce one SMART recommendation. Each must include:
1. The gap it addresses
2. The brief signal that justifies it
3. The SMART-compliant action
4. A priority level
5. A feasibility note (especially if resources or baselines are unknown)

---

## OUTPUT FORMAT

---

### ⚠️ Missing Context *(include only if inputs are incomplete)*
> List any missing elements that would improve recommendation quality. Do not block output — proceed with available data and flag gaps here.

---

### 🏷️ Brand Context Snapshot
- **Brand:** [Name] — [Industry]
- **Current plan focus:** [Summary]
- **Brief signals:** [Summary]
- **Primary gap:** [One-line diagnosis]

---

### 📋 SMART Improvement Recommendations

| # | Gap Identified | Brief Signal | SMART Recommendation | Priority | Feasibility Note |
|---|---------------|--------------|----------------------|----------|-----------------|
| 1 | | | | CRITICAL | |
| 2 | | | | HIGH | |
| 3 | | | | MEDIUM | |
| 4 | | | | LOW | |

**Priority definitions:**
- **CRITICAL** — Directly impacts campaign performance or audience retention; act within current cycle
- **HIGH** — Significant opportunity with clear brief support; act within 30 days
- **MEDIUM** — Valuable but not urgent; plan for next editorial cycle
- **LOW** — Nice-to-have; revisit at quarterly review

---

### ✅ Preserved Strengths
What the current plan does well and should not be changed or disrupted.

---

### 🚩 Flagged Recommendations *(include only if applicable)*
Recommendations that were considered but flagged as **OPTIMISTIC**, **off-brand**, or **resource-heavy** — with a conservative alternative for each.

---

### 🔁 Suggested Next Steps
Three immediate actions for the editorial team, ordered by priority.

---

## CONSTRAINTS

- Never invent data not present in either document
- Every recommendation must trace back to BOTH the plan AND the brief
- Never produce a recommendation that doesn't fit the brand's natural content territory without explicitly flagging it
- If a KPI feels inflated relative to the brand's scale, apply the Achievability Check and flag it
- Output must be usable by a marketer, not a strategy consultant — keep language direct and operational
- Do not produce more than 6 recommendations unless the brief explicitly surfaces more than 6 distinct gaps

---

## EXAMPLE TRANSFORMATION

**Raw output (before this agent):**
> Publish a bi-weekly series highlighting Tunisian achievements abroad, with a minimum of 2 articles per month, starting May 15th, and aiming for a 20% increase in engagement on social media channels within the next 3 months

**Agent-improved version (for a consumer soft drinks brand):**
> Launch a bi-weekly social media spotlight series featuring Tunisian personalities and achievements abroad, tied to brand values around local pride. Format: short-form video or carousel posts on Instagram and Facebook. Target: 2 posts/month minimum. KPI: 15% increase in post saves and shares (stronger brand affinity signal than raw engagement for this category) within 3 months. Start date: May 15th. ⚠️ *Feasibility note: confirm video production capacity before committing to video format — static carousel is an acceptable fallback.*

---

*This agent does not retain any brand or client data between sessions.*
"""

# ── Token budget constants ─────────────────────────────────────────────────────
MAX_PLAN_CHARS = 6000   # ~1 500 tokens — keep Groq within free-tier budget


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
    return file_bytes.decode("utf-8", errors="replace")


# ── Prompt construction ────────────────────────────────────────────────────────

def _format_analyst_brief(analyst_output: dict) -> str:
    """Serialize the full analyst brief as-is into the prompt."""
    return "## ANALYST BRIEF\n\n" + json.dumps(analyst_output, ensure_ascii=False, indent=2)


def _format_brand_context(brand_context: dict) -> str:
    """Render brand context fields as a markdown block."""
    lines = ["## BRAND CONTEXT\n"]
    labels = {
        "brand_name": "Brand Name",
        "slogan": "Slogan",
        "brand_desc": "Brand Description",
        "raison_detre": "Raison d'être",
        "product_name": "Product Name",
        "product_desc": "Product Description",
    }
    for key, label in labels.items():
        if brand_context.get(key):
            lines.append(f"- **{label}:** {brand_context[key]}")
    return "\n".join(lines)


def _build_user_prompt(analyst_output: dict, redaction_plan: str) -> str:
    """Combine analyst brief, optional brand context, and redaction plan into the prompt."""
    truncated_plan = (
        redaction_plan[:MAX_PLAN_CHARS] + "\n\n[…document truncated for token budget…]"
        if len(redaction_plan) > MAX_PLAN_CHARS
        else redaction_plan
    )

    # Separate brand context from the rest of the analyst output
    brand_context = analyst_output.pop("brand_context", None) if isinstance(analyst_output, dict) else None
    brief_block = _format_analyst_brief(analyst_output)

    parts = [brief_block]
    if brand_context:
        parts.append(_format_brand_context(brand_context))

    parts += [
        "---",
        "## REDACTION PLAN (Editorial Calendar)\n",
        truncated_plan,
        "---",
        "Cross-reference the analyst brief and the redaction plan above. "
        "Produce the full Editorial Plan Improvement Report following your output format exactly.",
    ]

    return "\n\n".join(parts)


# ── Response parsing ───────────────────────────────────────────────────────────

def _parse_table_rows(table_text: str) -> list[dict]:
    """Parse a 6-column SMART recommendations markdown table into row dicts."""
    rows = []
    for line in table_text.splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|[-| :]+\|$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        # Skip the header row (number column is "#" or non-numeric)
        if not cells[0].strip().lstrip('0123456789').strip() == '' or cells[0].strip() == '':
            continue
        rows.append({
            "number": cells[0],
            "gap_identified": cells[1],
            "brief_signal": cells[2],
            "smart_recommendation": cells[3],
            "priority": cells[4],
            "feasibility_note": cells[5] if len(cells) > 5 else "",
        })
    return rows


# Matches ### [emoji] Section Title or **Section Title** headers, then captures until next --- or end
_SECTION_RE = re.compile(
    r"###\s*[^\w\n]*(?P<title>[^\n]+)\n(?P<body>.*?)(?=\n---|\n###\s|\Z)",
    re.DOTALL,
)


def _extract_emoji_section(raw: str, keyword: str) -> str:
    """Extract body of the section whose title contains `keyword` (case-insensitive)."""
    for m in _SECTION_RE.finditer(raw):
        if keyword.lower() in m.group("title").lower():
            return m.group("body").strip()
    return ""


_MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists", "nl2br"]

# Strip these two sections before building html_body / html_rest
_SMART_SECTION_RE = re.compile(
    r"###\s*.{0,10}SMART\s+Improvement\s+Recommendations.+?(?=\n###\s|\Z)",
    re.DOTALL | re.IGNORECASE,
)
_BRAND_SECTION_RE = re.compile(
    r"###\s*.{0,10}Brand\s+Context\s+Snapshot.+?(?=\n###\s|\Z)",
    re.DOTALL | re.IGNORECASE,
)


def _md_to_html(raw: str) -> str:
    """Convert the LLM markdown report to semantic HTML."""
    return md_lib.markdown(raw, extensions=_MD_EXTENSIONS)


def _parse_report(raw: str) -> dict:
    """
    Parse the Editorial Plan Improvement Report into structured fields.

    Returns::

        {
            "html_output": str,               # full report as rendered HTML
            "raw_markdown": str,
            "missing_context": str,
            "brand_context_snapshot": str,
            "recommendations": [
                { number, gap_identified, brief_signal,
                  smart_recommendation, priority, feasibility_note }
            ],
            "preserved_strengths": str,
            "flagged_recommendations": str,
            "suggested_next_steps": str,
        }
    """
    html_output = _md_to_html(raw)

    missing_context = _extract_emoji_section(raw, "Missing Context")
    brand_snapshot = _extract_emoji_section(raw, "Brand Context Snapshot")

    # html_missing_context: just the Missing Context section as HTML
    html_missing_context = _md_to_html(missing_context) if missing_context else ""

    # html_brand_context: just the Brand Context Snapshot section as HTML
    html_brand_context = _md_to_html(brand_snapshot) if brand_snapshot else ""

    # html_body: full report minus the SMART table (backward compat)
    raw_no_smart = _SMART_SECTION_RE.sub("", raw).strip()
    html_body = _md_to_html(raw_no_smart)

    # html_rest: everything except Brand Context Snapshot AND SMART table AND Missing Context
    # (rendered between the visual cards and nothing else)
    _MISSING_SECTION_RE = re.compile(
        r"###\s*.{0,10}Missing\s+Context.+?(?=\n###\s|\Z)",
        re.DOTALL | re.IGNORECASE,
    )
    raw_rest = _BRAND_SECTION_RE.sub("", raw_no_smart)
    raw_rest = _MISSING_SECTION_RE.sub("", raw_rest).strip()
    html_rest = _md_to_html(raw_rest)

    preserved = _extract_emoji_section(raw, "Preserved Strengths")
    flagged = _extract_emoji_section(raw, "Flagged Recommendations")
    next_steps = _extract_emoji_section(raw, "Suggested Next Steps")

    table_match = re.search(
        r"SMART Improvement Recommendations[^\n]*\n((?:.*\n)*?\|.*?)(?=\n---|\n###|\Z)",
        raw,
        re.IGNORECASE | re.DOTALL,
    )
    recommendations = _parse_table_rows(table_match.group(1)) if table_match else []

    return {
        "html_output": html_output,
        "html_body": html_body,
        "html_brand_context": html_brand_context,
        "html_missing_context": html_missing_context,
        "html_rest": html_rest,
        "raw_markdown": raw,
        "missing_context": missing_context,
        "brand_context_snapshot": brand_snapshot,
        "recommendations": recommendations,
        "preserved_strengths": preserved,
        "flagged_recommendations": flagged,
        "suggested_next_steps": next_steps,
    }


# ── Public API ────────────────────────────────────────────────────────────────

def audit(redaction_plan: str, analyst_output: dict) -> dict:
    """
    Cross-reference the analyst brief with the redaction plan and return
    a SMART Editorial Plan Improvement Report.

    ``analyst_output`` is the full structured brief from the Analyst Agent.
    ``redaction_plan`` is the editorial calendar text uploaded by the marketer.

    Returns::

        {
            "raw_markdown": str,
            "missing_context": str,
            "brand_context_snapshot": str,
            "recommendations": [ {number, gap_identified, brief_signal,
                                   smart_recommendation, priority, feasibility_note} ],
            "preserved_strengths": str,
            "flagged_recommendations": str,
            "suggested_next_steps": str,
        }
    """
    if not redaction_plan.strip():
        raise ValueError("redaction_plan must not be empty.")

    user_prompt = _build_user_prompt(analyst_output, redaction_plan)
    logger.info("[Strategist] Running editorial audit")

    raw_response = call_llm(SYSTEM_PROMPT, user_prompt)
    logger.debug("[Strategist] Raw LLM response:\n%s", raw_response)

    return _parse_report(raw_response)
