import logging
import time

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.hotspot import Hotspot
from app.models.hotspot_dentist import HotspotDentist
from app.services.google_places import GooglePlacesClient

logger = logging.getLogger(__name__)


DENTIST_KEYWORDS = ["diş", "dental", "dent"]


def count_dentists_for_area(session: Session, area_id: int) -> list[HotspotDentist]:
    client = GooglePlacesClient(session)
    settings = get_settings()
    hotspots = session.query(Hotspot).filter_by(area_id=area_id).all()

    results: list[HotspotDentist] = []

    for hotspot in hotspots:
        count = 0
        for keyword in DENTIST_KEYWORDS:
            pagetoken = None
            while True:
                payload = client.text_search(
                    query=keyword,
                    location=f"{hotspot.lat},{hotspot.lng}",
                    radius_m=settings.dentist_search_radius_m,
                    pagetoken=pagetoken,
                )
                count += len(payload.get("results", []))
                pagetoken = payload.get("next_page_token")
                if not pagetoken:
                    break
                time.sleep(2)

        dentist_count = HotspotDentist(hotspot_id=hotspot.id, dentist_count=count)
        session.add(dentist_count)
        results.append(dentist_count)

    session.commit()
    logger.info("Stored dentist counts for %s hotspots", len(results))
    return results
