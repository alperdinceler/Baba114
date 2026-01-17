from sqlalchemy import JSON, Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class Hotspot(Base):
    __tablename__ = "hotspots"

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    crowd_score = Column(Float, nullable=False)
    meta_json = Column(JSON, nullable=True)

    area = relationship("Area", backref="hotspots")
