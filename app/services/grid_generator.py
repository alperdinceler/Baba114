import logging
import math
from typing import Iterable

from sqlalchemy.orm import Session

from app.models.grid_point import GridPoint
from app.utils.geo import bbox_from_polygon

logger = logging.getLogger(__name__)


def generate_grid_points(
    bbox: dict,
    step_m: int,
) -> list[tuple[float, float]]:
    min_lat = bbox["min_lat"]
    max_lat = bbox["max_lat"]
    min_lng = bbox["min_lng"]
    max_lng = bbox["max_lng"]

    lat_step = step_m / 111_320
    points: list[tuple[float, float]] = []

    lat = min_lat
    while lat <= max_lat:
        lng_step = step_m / (111_320 * math.cos(math.radians(lat)) or 1)
        lng = min_lng
        while lng <= max_lng:
            points.append((lat, lng))
            lng += lng_step
        lat += lat_step

    return points


def store_grid_points(
    session: Session,
    area_id: int,
    bbox: dict,
    step_m: int,
) -> list[GridPoint]:
    points = generate_grid_points(bbox, step_m)
    grid_points = [GridPoint(area_id=area_id, lat=lat, lng=lng) for lat, lng in points]
    session.query(GridPoint).filter_by(area_id=area_id).delete()
    session.add_all(grid_points)
    session.commit()
    logger.info("Stored %s grid points for area %s", len(grid_points), area_id)
    return grid_points


def resolve_bbox(bbox: dict | None, polygon: Iterable[Iterable[float]] | None) -> dict:
    if bbox:
        return bbox
    if polygon:
        return bbox_from_polygon(polygon)
    raise ValueError("Either bbox or polygon is required")
