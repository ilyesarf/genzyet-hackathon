# Data Analyst Agent

LLM-powered intelligence layer that sits on top of the **Scraper API**, analyses recently ingested articles, and exposes structured results via a FastAPI endpoint.

## Architecture

```
Scraper API  ──►  analyst_agent  ──►  Frontend / Client
 (port 8000)       (port 8001)
```

The agent calls the Scraper API to fetch articles, passes them through an LLM (Groq → Gemini fallback), parses the markdown output into structured JSON, and serves it.

## Quick Start

### 1. Install dependencies

```bash
cd analyst_agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

| Variable          | Description                                  | Default                 |
|-------------------|----------------------------------------------|-------------------------|
| `GROQ_API_KEY`    | API key for Groq (primary LLM)               | —                       |
| `GEMINI_API_KEY`  | API key for Google Gemini (fallback LLM)      | —                       |
| `SCRAPER_API_URL` | Base URL of the Scraper API                   | `http://localhost:8000` |

### 3. Run the server

Make sure the **Scraper API** is already running on its configured port, then:

```bash
uvicorn api:app --host 0.0.0.0 --port 8001 --reload
```

## API Reference

### `GET /analyze`

Analyse articles already stored in the Scraper DB.

| Param      | Type   | Default | Description              |
|------------|--------|---------|--------------------------|
| `window`   | int    | `24`    | Time window in hours     |
| `category` | string | `null`  | Filter by category       |

```bash
# All articles from the last 24 hours
curl http://localhost:8001/analyze

# Tech articles from the last 12 hours
curl "http://localhost:8001/analyze?window=12&category=tech"
```

### `POST /analyze/refresh`

Trigger a live scrape **then** analyse the fresh data.

| Param      | Type   | Default | Description              |
|------------|--------|---------|--------------------------|
| `window`   | int    | `24`    | Time window in hours     |
| `category` | string | `null`  | Filter by category       |

```bash
# Scrape + analyse everything
curl -X POST http://localhost:8001/analyze/refresh

# Scrape + analyse tech only, last 6 hours
curl -X POST "http://localhost:8001/analyze/refresh?window=6&category=tech"
```

### Response Shape

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "headline": "Concise rewritten headline",
        "source": "Source Name",
        "date": "2026-05-01",
        "why_it_matters": "Marketing impact summary",
        "relevance_score": "High"
      }
    ],
    "tldr": [
      "Actionable insight #1",
      "Actionable insight #2"
    ]
  }
}
```

### Error Codes

| Code | Meaning                                        |
|------|------------------------------------------------|
| 502  | All LLM backends failed (Groq + Gemini)        |
| 503  | Scraper API unreachable or analysis error       |

## LLM Fallback

The agent tries **Groq** (`llama-3.3-70b-versatile`) first. If Groq fails for any reason (quota, timeout, network), it automatically falls back to **Google Gemini** (`gemini-1.5-flash`). If both fail, a `502` is returned.

## Project Structure

```
analyst_agent/
├── api.py            # FastAPI endpoints
├── agent.py          # Core analysis logic + Scraper API client
├── llm.py            # LLM abstraction (Groq → Gemini fallback)
├── .env.example      # Environment template
├── requirements.txt  # Pinned dependencies
└── README.md         # This file
```
