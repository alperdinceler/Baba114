from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class HotspotDentist(Base):
    __tablename__ = "hotspot_dentists"

    id = Column(Integer, primary_key=True)
    hotspot_id = Column(Integer, ForeignKey("hotspots.id"), nullable=False)
    counted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    dentist_count = Column(Integer, nullable=False)

    hotspot = relationship("Hotspot", backref="dentist_counts")
