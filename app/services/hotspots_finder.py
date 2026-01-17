import logging
import time

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.hotspot import Hotspot
from app.models.hotspot_poi import HotspotPoi
from app.services.google_places import GooglePlacesClient

logger = logging.getLogger(__name__)


def compute_crowd_score(poi_count: int, ratings_total_sum: int, avg_rating: float) -> float:
    settings = get_settings()
    weights = settings.hotspot_weights
    return (
        weights.w_poi_count * poi_count
        + weights.w_ratings_total * ratings_total_sum
        + weights.w_avg_rating * avg_rating
    )


def find_hotspots(
    session: Session,
    area_id: int,
    grid_points: list[tuple[float, float]],
    top_n: int,
    poi_types: list[str],
) -> list[Hotspot]:
    client = GooglePlacesClient(session)
    hotspots: list[tuple[Hotspot, list[dict]]] = []

    for lat, lng in grid_points:
        location = f"{lat},{lng}"
        poi_results: list[dict] = []
        for poi_type in poi_types:
            payload = client.nearby_search(location=location, radius_m=1000, place_type=poi_type)
            poi_results.extend(payload.get("results", []))
            time.sleep(0.1)

        if not poi_results:
            continue

        poi_count = len(poi_results)
        ratings_total_sum = sum(result.get("user_ratings_total", 0) for result in poi_results)
        avg_rating = (
            sum(result.get("rating", 0) for result in poi_results) / poi_count
        )
        crowd_score = compute_crowd_score(poi_count, ratings_total_sum, avg_rating)
        hotspots.append(
            (
                Hotspot(
                    area_id=area_id,
                    lat=lat,
                    lng=lng,
                    crowd_score=crowd_score,
                    meta_json={"poi_count": poi_count, "avg_rating": avg_rating},
                ),
                poi_results,
            )
        )

    if not hotspots:
        return []

    hotspots.sort(key=lambda item: item[0].crowd_score, reverse=True)
    top_hotspots = hotspots[:top_n]

    session.query(Hotspot).filter_by(area_id=area_id).delete()
    session.query(HotspotPoi).delete()
    session.add_all([hotspot for hotspot, _ in top_hotspots])
    session.flush()

    for hotspot, poi_results in top_hotspots:
        pois = [
            HotspotPoi(
                hotspot_id=hotspot.id,
                place_id=result.get("place_id"),
                name=result.get("name", ""),
                types=result.get("types", []),
                rating=result.get("rating"),
                ratings_total=result.get("user_ratings_total"),
            )
            for result in poi_results
        ]
        session.add_all(pois)

    session.commit()
    logger.info("Stored %s hotspots for area %s", len(top_hotspots), area_id)
    return [hotspot for hotspot, _ in top_hotspots]
