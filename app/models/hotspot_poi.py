from sqlalchemy import JSON, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class HotspotPoi(Base):
    __tablename__ = "hotspot_pois"

    id = Column(Integer, primary_key=True)
    hotspot_id = Column(Integer, ForeignKey("hotspots.id"), nullable=False)
    place_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    types = Column(JSON, nullable=False)
    rating = Column(Float, nullable=True)
    ratings_total = Column(Integer, nullable=True)

    hotspot = relationship("Hotspot", backref="pois")
