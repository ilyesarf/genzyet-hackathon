"""
FastAPI application for the Data Analyst Agent.

Endpoints
---------
GET  /analyze?window=24&category=tech   — analyse cached articles
POST /analyze/refresh?window=24&category=tech — scrape first, then analyse
"""

import logging
from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agent import analyze, refresh_and_analyze
from llm import LLMError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Data Analyst Agent API",
    description=(
        "Intelligence layer that sits on top of the Scraper API, "
        "adds LLM-powered analysis, and exposes structured results."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/analyze", summary="Analyse recent articles")
def get_analyze(
    window: int = Query(24, ge=1, description="Time window in hours"),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """
    Fetch articles from the Scraper API within the given time window,
    run them through the LLM analyst, and return structured results.
    """
    try:
        result = analyze(window_hours=window, category=category)
        return JSONResponse(content={"status": "success", "data": result})
    except LLMError as exc:
        logger.error("LLM backends exhausted: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="All LLM backends failed. Please try again later.",
        )
    except Exception as exc:
        logger.error("Analysis failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=f"Analysis failed: {exc}",
        )


@app.post("/analyze/refresh", summary="Scrape then analyse")
def post_analyze_refresh(
    window: int = Query(24, ge=1, description="Time window in hours"),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """
    Trigger a live scrape on the Scraper API, then run LLM analysis
    on the freshly ingested data.
    """
    try:
        result = refresh_and_analyze(window_hours=window, category=category)
        return JSONResponse(content={"status": "success", "data": result})
    except LLMError as exc:
        logger.error("LLM backends exhausted: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="All LLM backends failed. Please try again later.",
        )
    except Exception as exc:
        logger.error("Refresh + analysis failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=f"Refresh and analysis failed: {exc}",
        )
