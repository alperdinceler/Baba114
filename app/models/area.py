from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String

from app.db.base import Base


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    bbox = Column(JSON, nullable=True)
    polygon = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
