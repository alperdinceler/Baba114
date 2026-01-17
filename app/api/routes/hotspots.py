from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db_session
from app.models.area import Area
from app.schemas.hotspot import DentistRunRequest, HotspotRunRequest
from app.services.dentists_counter import count_dentists_for_area
from app.services.grid_generator import resolve_bbox, store_grid_points
from app.services.hotspots_finder import find_hotspots

router = APIRouter()


@router.post("/hotspots/run")
def run_hotspots(payload: HotspotRunRequest, db: Session = Depends(get_db_session)) -> dict:
    settings = get_settings()
    area = db.query(Area).filter_by(id=payload.area_id).one_or_none()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")

    bbox = resolve_bbox(area.bbox, area.polygon)
    grid_points = store_grid_points(db, area.id, bbox, payload.grid_step_m)
    hotspots = find_hotspots(
        db,
        area_id=area.id,
        grid_points=[(gp.lat, gp.lng) for gp in grid_points],
        top_n=payload.top_n,
        poi_types=settings.default_poi_types,
    )
    return {"hotspots": len(hotspots)}


@router.post("/dentists/run")
def run_dentists(payload: DentistRunRequest, db: Session = Depends(get_db_session)) -> dict:
    area = db.query(Area).filter_by(id=payload.area_id).one_or_none()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    counts = count_dentists_for_area(db, area.id)
    return {"hotspots": len(counts)}
