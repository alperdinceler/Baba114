from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.area import Area
from app.schemas.area import AreaCreate, AreaOut

router = APIRouter()


@router.post("/areas", response_model=AreaOut)
def create_area(payload: AreaCreate, db: Session = Depends(get_db_session)) -> AreaOut:
    if not payload.bbox and not payload.polygon:
        raise HTTPException(status_code=400, detail="bbox or polygon is required")

    area = Area(name=payload.name, bbox=payload.bbox, polygon=payload.polygon)
    db.add(area)
    db.commit()
    db.refresh(area)
    return area
