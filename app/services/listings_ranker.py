import logging
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.hotspot import Hotspot
from app.models.hotspot_dentist import HotspotDentist
from app.models.listing import Listing
from app.models.listing_score import ListingScore
from app.utils.geo import haversine_distance_m

logger = logging.getLogger(__name__)


@dataclass
class ListingFilter:
    max_rent: float | None = None
    min_m2: float | None = None
    max_distance_to_hotspot: float | None = None
    min_dentist_count: int | None = None
    min_crowd_score: float | None = None


def _latest_dentist_count(hotspot: Hotspot) -> int:
    counts = hotspot.dentist_counts
    if not counts:
        return 0
    return max(counts, key=lambda item: item.counted_at).dentist_count


def rank_listings(
    session: Session,
    area_id: int,
    listing_filter: ListingFilter,
) -> list[ListingScore]:
    settings = get_settings()
    weights = settings.listing_score_weights
    hotspots = session.query(Hotspot).filter_by(area_id=area_id).all()
    listings = session.query(Listing).all()
    scored: list[ListingScore] = []

    for listing in listings:
        if listing.price is not None and listing_filter.max_rent is not None:
            if listing.price > listing_filter.max_rent:
                continue
        if listing.m2 is not None and listing_filter.min_m2 is not None:
            if listing.m2 < listing_filter.min_m2:
                continue

        best_score = None
        best_hotspot = None
        best_distance = None

        for hotspot in hotspots:
            if listing.lat is None or listing.lng is None:
                continue
            distance = haversine_distance_m(listing.lat, listing.lng, hotspot.lat, hotspot.lng)
            if (
                listing_filter.max_distance_to_hotspot is not None
                and distance > listing_filter.max_distance_to_hotspot
            ):
                continue

            dentist_count = _latest_dentist_count(hotspot)
            if (
                listing_filter.min_dentist_count is not None
                and dentist_count < listing_filter.min_dentist_count
            ):
                continue

            if (
                listing_filter.min_crowd_score is not None
                and hotspot.crowd_score < listing_filter.min_crowd_score
            ):
                continue

            score = (
                weights.w_crowd_score * hotspot.crowd_score
                + weights.w_dentist_count * dentist_count
                - weights.w_rent * (listing.price or 0)
                - weights.w_distance * distance
            )

            if best_score is None or score > best_score:
                best_score = score
                best_hotspot = hotspot
                best_distance = distance

        if best_score is None or best_hotspot is None or best_distance is None:
            continue

        listing_score = ListingScore(
            listing_id=listing.id,
            hotspot_id=best_hotspot.id,
            distance_m=best_distance,
            score=best_score,
        )
        scored.append(listing_score)

    session.query(ListingScore).delete()
    session.add_all(scored)
    session.commit()
    logger.info("Ranked %s listings", len(scored))
    return scored


def build_response(
    listings: Iterable[ListingScore],
) -> list[dict]:
    response: list[dict] = []
    for item in listings:
        listing: Listing = item.listing
        hotspot: Hotspot = item.hotspot
        dentist_count = _latest_dentist_count(hotspot)
        response.append(
            {
                "listing_id": listing.id,
                "title": listing.title,
                "price": listing.price,
                "m2": listing.m2,
                "rooms": listing.rooms,
                "address": listing.address,
                "lat": listing.lat,
                "lng": listing.lng,
                "hotspot_id": hotspot.id,
                "distance_m": item.distance_m,
                "crowd_score": hotspot.crowd_score,
                "dentist_count": dentist_count,
                "score": item.score,
            }
        )
    return response
