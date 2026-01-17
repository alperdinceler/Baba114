# Hotspot → Dentist → Listings Pipeline

## Overview
This service provides a FastAPI + SQLite (default) or PostgreSQL pipeline to:
1. Generate grid points for a target area.
2. Find hotspots using the official Google Places API.
3. Count dentists around hotspots using text search queries.
4. Import listings from CSV/JSON export files.
5. Rank listings by proximity and business signals.

## Requirements
- Python 3.13
- SQLite (default) or PostgreSQL (optional)
- Google Places API key (Nearby Search / Text Search / Place Details)
- Optional: Google Geocoding API key (if geocoding addresses)

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

Create a database and update `.env` with your credentials (SQLite is the default).

## Environment Variables
```bash
DATABASE_URL=sqlite:///./hotspot.db
GOOGLE__API_KEY=your_key_here
GOOGLE__REQUEST_TIMEOUT_S=10
GOOGLE__MAX_RETRIES=5
GOOGLE__BACKOFF_BASE_S=1.0
GRID_STEP_M=500
DENTIST_SEARCH_RADIUS_M=1500
HOTSPOT_TOP_N=20
HOTSPOT_WEIGHTS__W_POI_COUNT=1.0
HOTSPOT_WEIGHTS__W_RATINGS_TOTAL=0.01
HOTSPOT_WEIGHTS__W_AVG_RATING=1.0
LISTING_SCORE_WEIGHTS__W_CROWD_SCORE=1.0
LISTING_SCORE_WEIGHTS__W_DENTIST_COUNT=1.0
LISTING_SCORE_WEIGHTS__W_RENT=0.001
LISTING_SCORE_WEIGHTS__W_DISTANCE=0.001
```

## Run API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Example Workflow
### Create Area
```bash
curl -X POST http://localhost:8000/areas \
  -H "Content-Type: application/json" \
  -d '{"name":"Kadikoy","bbox":{"min_lat":40.97,"min_lng":29.02,"max_lat":40.99,"max_lng":29.04}}'
```

### Run Hotspots
```bash
curl -X POST http://localhost:8000/hotspots/run \
  -H "Content-Type: application/json" \
  -d '{"area_id":1,"grid_step_m":500,"top_n":20}'
```

### Count Dentists
```bash
curl -X POST http://localhost:8000/dentists/run \
  -H "Content-Type: application/json" \
  -d '{"area_id":1}'
```

### Import Listings
```bash
curl -X POST http://localhost:8000/listings/import \
  -H "Content-Type: application/json" \
  -d '{"path":"data/listings.csv","source":"user_export"}'
```

### Search Listings
```bash
curl "http://localhost:8000/listings/search?area_id=1&max_rent=35000&min_m2=80&max_distance=1000"
```

## Notes
- This project avoids scraping. Only Google official APIs are used for Places/Geocoding.
- Listing imports rely on user-provided exports or official APIs/feeds.
- Place and geocode results are cached in the database tables `place_cache` and `geocode_cache`.
