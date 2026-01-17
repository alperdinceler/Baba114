from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.listing import ListingImportRequest
from app.services.listings_ingestor import ingest_listings
from app.services.listings_ranker import ListingFilter, build_response, rank_listings

router = APIRouter()


@router.post("/listings/import")
def import_listings(payload: ListingImportRequest, db: Session = Depends(get_db_session)) -> dict:
    if not payload.path:
        raise HTTPException(status_code=400, detail="path is required")
    listings = ingest_listings(db, payload.source, payload.path)
    return {"imported": len(listings)}


@router.get("/listings/search")
def search_listings(
    area_id: int,
    max_rent: float | None = None,
    min_m2: float | None = None,
    max_distance: float | None = None,
    min_dentist_count: int | None = None,
    min_crowd_score: float | None = None,
    db: Session = Depends(get_db_session),
) -> list[dict]:
    listing_filter = ListingFilter(
        max_rent=max_rent,
        min_m2=min_m2,
        max_distance_to_hotspot=max_distance,
        min_dentist_count=min_dentist_count,
        min_crowd_score=min_crowd_score,
    )
    scores = rank_listings(db, area_id, listing_filter)
    return build_response(scores)
