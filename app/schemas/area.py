from typing import Optional

from pydantic import BaseModel, Field


class AreaCreate(BaseModel):
    name: str = Field(..., example="Kadikoy")
    bbox: Optional[dict] = Field(
        default=None,
        description="Bounding box dict {min_lat, min_lng, max_lat, max_lng}",
    )
    polygon: Optional[list] = Field(
        default=None,
        description="List of [lng, lat] coordinates",
    )


class AreaOut(BaseModel):
    id: int
    name: str
    bbox: Optional[dict] = None
    polygon: Optional[list] = None

    class Config:
        from_attributes = True
