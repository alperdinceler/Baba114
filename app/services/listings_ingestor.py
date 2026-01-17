import csv
import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models.listing import Listing
from app.services.google_places import GooglePlacesClient

logger = logging.getLogger(__name__)


def _resolve_coordinates(client: GooglePlacesClient, address: str) -> tuple[float | None, float | None]:
    payload = client.geocode(address)
    results = payload.get("results", [])
    if not results:
        return None, None
    location = results[0]["geometry"]["location"]
    return location.get("lat"), location.get("lng")


def _parse_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [row for row in reader]


def _parse_json(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        return data.get("listings", [])
    return data


def ingest_listings(session: Session, source: str, path: str) -> list[Listing]:
    client = GooglePlacesClient(session)
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(path)

    if path_obj.suffix.lower() == ".csv":
        rows = _parse_csv(path_obj)
    elif path_obj.suffix.lower() in {".json", ".jsonl"}:
        rows = _parse_json(path_obj)
    else:
        raise ValueError("Unsupported file format. Use CSV or JSON")

    listings: list[Listing] = []
    for row in rows:
        lat = row.get("lat") or row.get("latitude")
        lng = row.get("lng") or row.get("longitude")
        address = row.get("address")
        if (not lat or not lng) and address:
            lat, lng = _resolve_coordinates(client, address)

        listing = Listing(
            source=source,
            title=row.get("title", ""),
            price=float(row["price"]) if row.get("price") else None,
            m2=float(row["m2"]) if row.get("m2") else None,
            rooms=row.get("rooms"),
            address=address,
            lat=float(lat) if lat else None,
            lng=float(lng) if lng else None,
            raw_json=row,
        )
        listings.append(listing)

    session.add_all(listings)
    session.commit()
    logger.info("Imported %s listings", len(listings))
    return listings
