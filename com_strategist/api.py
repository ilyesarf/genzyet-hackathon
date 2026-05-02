"""
FastAPI application for the COM Strategist Agent.

Endpoints
---------
POST /audit          — JSON body: analyst_output + redaction_plan text
POST /audit/upload   — multipart: analyst_output (JSON string) + redaction_plan file
GET  /history        — list all past audit records
POST /history        — save a new audit record
GET  /health         — liveness check
"""

import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent import audit, extract_text
from db import init_db, insert_record, get_all
from llm import LLMError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    init_db()
    yield


app = FastAPI(
    title="COM Strategist Agent API",
    description=(
        "Editorial strategy optimizer: cross-references the Analyst Agent's brief "
        "with a marketer's redaction plan and returns a SMART improvement report."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── JSON audit endpoint ────────────────────────────────────────────────────────

class AuditRequest(BaseModel):
    analyst_output: dict
    redaction_plan: str


@app.post("/audit", summary="Run an editorial audit (JSON input)")
def post_audit(body: AuditRequest):
    """
    Cross-reference the analyst brief with the redaction plan and return
    a SMART Editorial Plan Improvement Report.

    - **analyst_output**: full structured brief from the Analyst Agent
    - **redaction_plan**: full text of the editorial calendar / redaction plan
    """
    try:
        result = audit(
            redaction_plan=body.redaction_plan,
            analyst_output=body.analyst_output,
        )
        return JSONResponse(content={"status": "success", "data": result})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except LLMError as exc:
        logger.error("LLM backends exhausted: %s", exc)
        raise HTTPException(status_code=502, detail="All LLM backends failed. Please try again later.")
    except Exception as exc:
        logger.error("Audit failed: %s", exc)
        raise HTTPException(status_code=503, detail=f"Audit failed: {exc}")


# ── File-upload audit endpoint ─────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@app.post("/audit/upload", summary="Run an editorial audit (file upload)")
async def post_audit_upload(
    strategy_file: UploadFile = File(..., description="PDF, DOCX, TXT, or MD redaction plan"),
    analyst_output: Optional[str] = Form(None, description="JSON string of the Analyst Agent brief"),
    mode: str = Form("detail", description="Ignored — kept for frontend compatibility"),
    brand_name: Optional[str] = Form(None),
    slogan: Optional[str] = Form(None),
    brand_desc: Optional[str] = Form(None),
    raison_detre: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    product_desc: Optional[str] = Form(None),
):
    """
    Upload the redaction plan as a file and run the editorial audit.
    Supported: **PDF**, **DOCX**, **TXT**, **MD**
    """
    parsed_analyst: dict = {}
    if analyst_output:
        try:
            parsed_analyst = json.loads(analyst_output)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=422, detail=f"Invalid JSON in 'analyst_output': {exc}")

    brand_context = {k: v for k, v in {
        "brand_name": brand_name, "slogan": slogan, "brand_desc": brand_desc,
        "raison_detre": raison_detre, "product_name": product_name, "product_desc": product_desc,
    }.items() if v}
    if brand_context:
        parsed_analyst["brand_context"] = brand_context

    filename = strategy_file.filename or ""
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{suffix}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    file_bytes = await strategy_file.read()
    try:
        redaction_plan_text = extract_text(file_bytes, filename)
    except Exception as exc:
        logger.error("Text extraction failed for '%s': %s", filename, exc)
        raise HTTPException(status_code=422, detail=f"Could not extract text from file: {exc}")

    if not redaction_plan_text.strip():
        raise HTTPException(status_code=422, detail="The uploaded document is empty or unreadable.")

    try:
        result = audit(redaction_plan=redaction_plan_text, analyst_output=parsed_analyst)
        return JSONResponse(content={"status": "success", "data": result})
    except LLMError as exc:
        logger.error("LLM backends exhausted: %s", exc)
        raise HTTPException(status_code=502, detail="All LLM backends failed. Please try again later.")
    except Exception as exc:
        logger.error("Upload audit failed: %s", exc)
        raise HTTPException(status_code=503, detail=f"Audit failed: {exc}")


# ── History endpoints ──────────────────────────────────────────────────────────

class HistoryRecord(BaseModel):
    name: str
    file: str
    news_used: list[str] = []
    improvements: int = 0


@app.get("/history", summary="List all past audit records")
def get_history():
    """Return all saved audit records, most recent first."""
    return JSONResponse(content={"status": "success", "data": get_all()})


@app.post("/history", summary="Save an audit record")
def post_history(body: HistoryRecord):
    """Persist a completed audit to the history database."""
    record = insert_record(
        name=body.name,
        file=body.file,
        news_used=body.news_used,
        improvements=body.improvements,
    )
    return JSONResponse(content={"status": "success", "data": record})


# ── Health check ───────────────────────────────────────────────────────────────

@app.get("/health", summary="Health check")
def health():
    return {"status": "ok", "agent": "COM Strategist v2.0"}
