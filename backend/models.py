from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Campground(Base):
    __tablename__ = "campgrounds"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    park_id = Column(String(100))
    region = Column(String(100))
    url = Column(String(500))

    searches = relationship("Search", back_populates="campground")


class Search(Base):
    __tablename__ = "searches"

    id = Column(Integer, primary_key=True)
    campground_id = Column(Integer, ForeignKey("campgrounds.id"), nullable=False)
    site_type = Column(String(50))
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="active")

    campground = relationship("Campground", back_populates="searches")
    availability = relationship("Availability", back_populates="search", cascade="all, delete-orphan")


class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, ForeignKey("searches.id"), nullable=False)
    site_id = Column(String(100))
    site_name = Column(String(255))
    date = Column(Date)
    available = Column(Boolean)
    last_checked = Column(DateTime, default=datetime.utcnow)

    search = relationship("Search", back_populates="availability")
