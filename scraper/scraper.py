import json
import logging
import datetime
import os
from time import mktime
import feedparser
import requests
from bs4 import BeautifulSoup
from db import insert_article, prune_old_articles, get_all_sources
from facebook_scraper import scrape_facebook_page

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def parse_date(date_obj):
    if isinstance(date_obj, datetime.datetime):
        return date_obj
    return datetime.datetime.utcnow()

def scrape_rss(source):
    logger.info(f"Scraping RSS source: {source['name']}")
    try:
        feed = feedparser.parse(source['url'])
        for entry in feed.entries:
            title = entry.get('title', '')
            url = entry.get('link', '')
            body = entry.get('summary', '') or entry.get('description', '')
            
            published_at = datetime.datetime.utcnow()
            if 'published_parsed' in entry and entry.published_parsed:
                published_at = datetime.datetime.fromtimestamp(mktime(entry.published_parsed))
                
            if title and url:
                logger.info(f"Scraped article: {title} ({url})")
                insert_article(source['name'], url, title, body, source['category'], published_at)
    except Exception as e:
        logger.error(f"Error scraping RSS {source['name']}: {e}")

def scrape_html(source):
    logger.info(f"Scraping HTML source: {source['name']}")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(source['url'], headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title = soup.title.string if soup.title else 'No Title'
        
        # Simple heuristic to extract main text body
        paragraphs = soup.find_all('p')
        body = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        url = source['url']
        published_at = datetime.datetime.utcnow()
        
        logger.info(f"Scraped article: {title} ({url})")
        insert_article(source['name'], url, title, body, source['category'], published_at)
    except Exception as e:
        logger.error(f"Error scraping HTML {source['name']}: {e}")


def scrape_single_source(source):
    if not source.get('enabled', False):
        return
        
    stype = source.get('type')
    if stype == 'rss':
        scrape_rss(source)
    elif stype == 'html':
        scrape_html(source)
    elif stype == 'facebook':
        page_id = source.get('facebook_page_id')
        if page_id:
            posts = scrape_facebook_page(page_id, max_posts=10)
            for post in posts:
                insert_article(
                    source=source['name'],
                    url=post['url'],
                    title=post['title'],
                    body=post['body'],
                    category=source['category'],
                    published_at=post['published_at']
                )
        else:
            logger.warning(f"Facebook source {source['name']} is missing 'facebook_page_id'")
    else:
        logger.warning(f"Unknown source type: {stype} for {source['name']}")

def run_scrape():
    logger.info("Starting scrape run...")
    try:
        sources = get_all_sources()
    except Exception as e:
        logger.error(f"Could not load sources from database: {e}")
        return

    for source in sources:
        scrape_single_source(source)

    logger.info("Pruning old articles (older than 72h)...")
    prune_old_articles()
    logger.info("Scrape run completed.")

if __name__ == "__main__":
    run_scrape()
