# News Intelligence Data Ingestion & Storage

This module provides the data ingestion and storage layer for the news intelligence platform.

## Architecture

- **SQLite Database**: Automatically managed via `db.py`. Stores articles and ensures data uniqueness based on URLs.
- **Scraper Module**: Uses `feedparser` and `requests`+`BeautifulSoup` to extract article data. Deduplicates content and prunes data older than 72 hours.
- **Scheduler**: Utilizes `APScheduler` to run a daily scraping job.
- **API**: A `FastAPI` app exposing endpoints for the LLM agents and other services.

## Prerequisites

- Python 3.10+

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Copy the example environment file and customize it.
   ```bash
   cp .env.example .env
   ```
   You can set the daily scrape time in `.env` (e.g., `SCRAPE_TIME=07:00`).

3. **Populate Sources:**
   Review and update `sources.json`. This file contains the registry of sources to scrape. Ensure that `"enabled": true` is set for sources you wish to process. Supported source types:
   - `rss`
   - `html`
   - `facebook`

## Facebook Scraping (Apify)

We use the [Apify Facebook Pages Scraper](https://apify.com/apify/facebook-pages-scraper) to fetch recent posts from Facebook sources reliably.

1. **Get an API Token:**
   Sign up at [apify.com](https://apify.com). Go to **Settings → Integrations** and copy your personal API token.
2. **Configure Environment:**
   Add `APIFY_API_TOKEN=your_token` to your `.env` file.
3. **Add a Source:**
   Find the Facebook Page ID (usually the name in the URL, e.g., `mosaiquefm` for `https://facebook.com/mosaiquefm`). Add an entry to `sources.json`:
   ```json
   {
     "name": "Mosaique FM",
     "type": "facebook",
     "url": "https://www.facebook.com/mosaiquefm",
     "facebook_page_id": "mosaiquefm",
     "category": "tunisia-news",
     "enabled": true
   }
   ```

## Running the Components

**Start the API Server:**
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```
- Test `GET /articles?window=24&category=tech` to fetch articles.
- Test `POST /scrape` to manually trigger an immediate scrape.

**Start the Standalone Scheduler:**
```bash
python scheduler.py
```
This will start a background scheduler that triggers a scrape run daily at the time specified in `.env`.

**Run an Immediate Scrape (CLI):**
```bash
python scraper.py
```
