"""
FastAPI application for the COM Strategist Agent (Straton v1.2).

Endpoints
---------
POST /audit              — JSON body: strategy_text + optional analyst_output
POST /audit/upload       — multipart: strategy_file (PDF/DOCX/TXT) + form fields
"""

import json
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent import audit, extract_text
from llm import LLMError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="COM Strategist Agent API — Straton v1.2",
    description=(
        "CMI audit layer: takes the Analyst Agent's intelligence output and a "
        "marketer-uploaded communication strategy, then returns a structured "
        "Straton audit with D1-D4 optimizations."
    ),
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── JSON endpoint ──────────────────────────────────────────────────────────────

class AuditRequest(BaseModel):
    strategy_text: str
    analyst_output: Optional[dict] = None
    mode: str = "detail"
    window_hours: int = 24
    category: Optional[str] = None


@app.post("/audit", summary="Run a CMI audit (JSON input)")
def post_audit(body: AuditRequest):
    """
    Run Straton's 4-D audit on the provided communication strategy.

    - **strategy_text**: full text of the marketer's COM strategy document
    - **analyst_output**: pre-fetched analyst intelligence (optional — if omitted
      the agent calls the Analyst API automatically)
    - **mode**: `"basic"` for an agile review, `"detail"` for a full deep-dive
    - **window_hours**: time window passed to the Analyst API when auto-fetching
    - **category**: optional news category filter for auto-fetch
    """
    try:
        result = audit(
            strategy_text=body.strategy_text,
            analyst_output=body.analyst_output,
            mode=body.mode,
            window_hours=body.window_hours,
            category=body.category,
        )
        return JSONResponse(content={"status": "success", "data": result})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except LLMError as exc:
        logger.error("LLM backends exhausted: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="All LLM backends failed. Please try again later.",
        )
    except Exception as exc:
        logger.error("Audit failed: %s", exc)
        raise HTTPException(status_code=503, detail=f"Audit failed: {exc}")


# ── File-upload endpoint ───────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@app.post("/audit/upload", summary="Run a CMI audit (file upload)")
async def post_audit_upload(
    strategy_file: UploadFile = File(..., description="PDF, DOCX, TXT, or MD strategy document"),
    mode: str = Form("detail", description="'basic' or 'detail'"),
    analyst_output: Optional[str] = Form(
        None, description="JSON string of analyst output (auto-fetched if omitted)"
    ),
    window_hours: int = Form(24, description="Time window for auto-fetching analyst data"),
    category: Optional[str] = Form(None, description="News category filter"),
):
    """
    Upload the marketer's strategy document as a file and run Straton's audit.

    Supported file types: **PDF**, **DOCX**, **TXT**, **MD**

    - **strategy_file**: the communication strategy document
    - **mode**: `"basic"` or `"detail"` (default: detail)
    - **analyst_output**: optional pre-fetched JSON string from the Analyst Agent
    - **window_hours**: hours window passed to Analyst API when auto-fetching
    - **category**: optional news category filter
    """
    # Validate file extension
    filename = strategy_file.filename or ""
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{suffix}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    # Extract text from the uploaded file
    file_bytes = await strategy_file.read()
    try:
        strategy_text = extract_text(file_bytes, filename)
    except Exception as exc:
        logger.error("Text extraction failed for '%s': %s", filename, exc)
        raise HTTPException(
            status_code=422,
            detail=f"Could not extract text from the uploaded file: {exc}",
        )

    if not strategy_text.strip():
        raise HTTPException(
            status_code=422,
            detail="The uploaded document appears to be empty or unreadable.",
        )

    # Parse analyst_output if provided as a JSON string
    parsed_analyst: Optional[dict] = None
    if analyst_output:
        try:
            parsed_analyst = json.loads(analyst_output)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid JSON in 'analyst_output': {exc}",
            )

    try:
        result = audit(
            strategy_text=strategy_text,
            analyst_output=parsed_analyst,
            mode=mode,
            window_hours=window_hours,
            category=category,
        )
        return JSONResponse(content={"status": "success", "data": result})
    except LLMError as exc:
        logger.error("LLM backends exhausted: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="All LLM backends failed. Please try again later.",
        )
    except Exception as exc:
        logger.error("Upload audit failed: %s", exc)
        raise HTTPException(status_code=503, detail=f"Audit failed: {exc}")


# ── Health check ───────────────────────────────────────────────────────────────

@app.get("/health", summary="Health check")
def health():
    return {"status": "ok", "agent": "Straton v1.2"}
