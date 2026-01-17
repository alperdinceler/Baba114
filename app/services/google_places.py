import hashlib
import logging
from typing import Any, Optional

import requests
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.cache import GeocodeCache, PlaceCache
from app.utils.rate_limit import GoogleApiError, with_backoff

logger = logging.getLogger(__name__)


class GooglePlacesClient:
    def __init__(self, session: Session):
        self.session = session
        self.settings = get_settings()

    def _request(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.settings.google.base_url}/{path}"
        params = {**params, "key": self.settings.google.api_key}

        def call() -> requests.Response:
            return requests.get(url, params=params, timeout=self.settings.google.request_timeout_s)

        response = with_backoff(call)
        payload = response.json()
        status = payload.get("status")
        if status not in {"OK", "ZERO_RESULTS"}:
            raise GoogleApiError(f"Google API error: {status} - {payload.get('error_message')}")
        return payload

    def nearby_search(
        self,
        location: str,
        radius_m: int,
        place_type: Optional[str] = None,
        keyword: Optional[str] = None,
        pagetoken: Optional[str] = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "location": location,
            "radius": radius_m,
        }
        if place_type:
            params["type"] = place_type
        if keyword:
            params["keyword"] = keyword
        if pagetoken:
            params["pagetoken"] = pagetoken
        return self._request("place/nearbysearch/json", params)

    def text_search(
        self,
        query: str,
        location: str,
        radius_m: int,
        pagetoken: Optional[str] = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "query": query,
            "location": location,
            "radius": radius_m,
        }
        if pagetoken:
            params["pagetoken"] = pagetoken
        return self._request("place/textsearch/json", params)

    def place_details(self, place_id: str) -> dict[str, Any]:
        cached = self.session.query(PlaceCache).filter_by(place_id=place_id).one_or_none()
        if cached:
            return cached.payload
        payload = self._request("place/details/json", {"place_id": place_id})
        self.session.add(PlaceCache(place_id=place_id, payload=payload))
        self.session.commit()
        return payload

    def geocode(self, address: str) -> dict[str, Any]:
        address_hash = hashlib.sha256(address.encode("utf-8")).hexdigest()
        cached = (
            self.session.query(GeocodeCache).filter_by(address_hash=address_hash).one_or_none()
        )
        if cached:
            return cached.payload
        payload = self._request("geocode/json", {"address": address})
        self.session.add(
            GeocodeCache(address_hash=address_hash, address=address, payload=payload)
        )
        self.session.commit()
        return payload
