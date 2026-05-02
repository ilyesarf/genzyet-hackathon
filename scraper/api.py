from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging

from scraper import run_scrape
import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import threading
from scheduler import start_scheduler

app = FastAPI(title="News Intelligence API", description="API for managing data ingestion layer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    logger.info("Starting scheduler...")
    start_scheduler()
    
    # Check if DB is empty; if so, trigger a scrape in the background
    try:
        articles = db.get_articles(window_hours=100000)
        if not articles:
            logger.info("Database is empty. Triggering initial scrape in background...")
            threading.Thread(target=run_scrape, daemon=True).start()
    except Exception as e:
        logger.error(f"Failed to check DB on startup: {e}")

@app.post("/scrape", summary="Trigger a scrape run on-demand")
def trigger_scrape():
    try:
        run_scrape()
        return {"status": "success", "message": "Scrape completed successfully."}
    except Exception as e:
        logger.error(f"Scrape trigger failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during scrape")

@app.get("/articles", summary="Get stored articles")
def get_articles(window: int = Query(24, description="Time window in hours"), 
                 category: Optional[str] = Query(None, description="Filter by category")):
    try:
        articles = db.get_articles(window_hours=window, category=category)
        return {"status": "success", "data": articles}
    except Exception as e:
        logger.error(f"Failed to get articles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching articles")

class SourceCreate(BaseModel):
    name: str
    type: str
    url: str
    category: str
    facebook_page_id: Optional[str] = None
    enabled: bool = True

class SourceToggle(BaseModel):
    enabled: bool

@app.get("/sources", summary="Get configured sources")
def get_sources():
    try:
        sources = db.get_all_sources()
        for s in sources:
            s['enabled'] = bool(s['enabled'])
        return {"status": "success", "data": sources}
    except Exception as e:
        logger.error(f"Failed to fetch sources: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching sources")

@app.post("/sources", summary="Add a new source")
def add_source(source: SourceCreate):
    try:
        db.add_source(
            name=source.name,
            stype=source.type,
            url=source.url,
            category=source.category,
            facebook_page_id=source.facebook_page_id,
            enabled=source.enabled
        )
        return {"status": "success", "message": "Source added successfully."}
    except Exception as e:
        logger.error(f"Failed to add source: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while adding source")

@app.patch("/sources/{source_id}/toggle", summary="Toggle a source's enabled status")
def toggle_source(source_id: int, toggle: SourceToggle):
    try:
        success = db.toggle_source(source_id, toggle.enabled)
        if not success:
            raise HTTPException(status_code=404, detail="Source not found")
        return {"status": "success", "message": f"Source {'enabled' if toggle.enabled else 'disabled'} successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle source: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while toggling source")
