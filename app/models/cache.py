from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String

from app.db.base import Base


class PlaceCache(Base):
    __tablename__ = "place_cache"

    id = Column(Integer, primary_key=True)
    place_id = Column(String(255), unique=True, nullable=False)
    payload = Column(JSON, nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class GeocodeCache(Base):
    __tablename__ = "geocode_cache"

    id = Column(Integer, primary_key=True)
    address_hash = Column(String(255), unique=True, nullable=False)
    address = Column(String(500), nullable=False)
    payload = Column(JSON, nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)
