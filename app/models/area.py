from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    bbox = Column(JSONB, nullable=True)
    polygon = Column(JSONB, nullable=True)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
