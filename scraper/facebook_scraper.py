import os
import logging
from datetime import datetime
from apify_client import ApifyClient

# Setup logging
logger = logging.getLogger(__name__)

# Check for API token at import time
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
if not APIFY_API_TOKEN:
    raise EnvironmentError("APIFY_API_TOKEN is not set in the environment variables.")

client = ApifyClient(APIFY_API_TOKEN)

def scrape_facebook_page(page_id: str, max_posts: int = 10) -> list[dict]:
    """
    Scrapes a Facebook page using the Apify Facebook Pages Scraper actor.
    """
    logger.info(f"Starting Apify scrape for Facebook page: {page_id}")
    try:
        run_input = {
            "startUrls": [{"url": f"https://www.facebook.com/{page_id}"}],
            "resultsLimit": max_posts,
            "maxPostsPerPage": max_posts
        }
        
        # Synchronously call the actor
        run = client.actor("KoJrdxJCTtpon81KY").call(run_input=run_input)
        
        # Fetch results from the dataset
        dataset_id = run["defaultDatasetId"]
        items = client.dataset(dataset_id).list_items().items
        
        posts = []
        for item in items:
            body = item.get("text") or item.get("message")
            if not body:
                continue
                
            title = item.get("pageName") or "Facebook Post"
            url = item.get("url") or item.get("postUrl") or f"https://www.facebook.com/{page_id}"
            
            # Parse datetime if available
            date_str = item.get("time") or item.get("date")
            published_at = datetime.utcnow()
            if date_str:
                try:
                    # Apify typically returns ISO formatted strings
                    # Replace 'Z' with '+00:00' for fromisoformat compatibility in older Python versions
                    date_str = date_str.replace("Z", "+00:00")
                    published_at = datetime.fromisoformat(date_str)
                except Exception as e:
                    logger.warning(f"Failed to parse date '{date_str}' for post {url}: {e}")
                    
            posts.append({
                "title": title,
                "body": body,
                "url": url,
                "published_at": published_at
            })
            
        logger.info(f"Successfully scraped {len(posts)} posts from Facebook page: {page_id}")
        return posts
        
    except Exception as e:
        logger.error(f"Error scraping Facebook page {page_id} via Apify: {e}")
        return []
