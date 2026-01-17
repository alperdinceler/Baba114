from sqlalchemy import JSON, Column, Float, Integer, String

from app.db.base import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True)
    source = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    price = Column(Float, nullable=True)
    m2 = Column(Float, nullable=True)
    rooms = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    raw_json = Column(JSON, nullable=True)
