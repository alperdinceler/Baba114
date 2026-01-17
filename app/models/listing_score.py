from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class ListingScore(Base):
    __tablename__ = "listing_scores"

    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    hotspot_id = Column(Integer, ForeignKey("hotspots.id"), nullable=False)
    distance_m = Column(Float, nullable=False)
    score = Column(Float, nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    listing = relationship("Listing", backref="scores")
    hotspot = relationship("Hotspot", backref="listing_scores")
