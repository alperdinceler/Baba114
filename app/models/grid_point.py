from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class GridPoint(Base):
    __tablename__ = "grid_points"

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    area = relationship("Area", backref="grid_points")
