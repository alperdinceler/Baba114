from typing import Optional

from pydantic import BaseModel, Field


class ListingImportRequest(BaseModel):
    path: Optional[str] = Field(default=None, description="Filesystem path to CSV/JSON")
    source: str = Field(default="user_upload")


class ListingSearchResponse(BaseModel):
    listing_id: int
    title: str
    price: Optional[float]
    m2: Optional[float]
    rooms: Optional[str]
    address: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    hotspot_id: int
    distance_m: float
    crowd_score: float
    dentist_count: int
    score: float
