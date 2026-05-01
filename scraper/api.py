from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from scraper import run_scrape
import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="News Intelligence API", description="API for managing data ingestion layer")

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
