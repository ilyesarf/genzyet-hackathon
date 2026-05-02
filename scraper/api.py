from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

import os
import json

@app.get("/sources", summary="Get configured sources")
def get_sources():
    sources_file = os.path.join(os.path.dirname(__file__), 'sources.json')
    try:
        if os.path.exists(sources_file):
            with open(sources_file, 'r') as f:
                sources = json.load(f)
            return {"status": "success", "data": sources}
        return {"status": "success", "data": []}
    except Exception as e:
        logger.error(f"Failed to read sources.json: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching sources")
