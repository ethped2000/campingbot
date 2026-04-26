from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from pydantic import BaseModel
from models import Search, Campground, Availability
from database import get_db

router = APIRouter(prefix="/api/searches", tags=["searches"])


class SearchCreate(BaseModel):
    campground_id: int
    site_type: Optional[str] = None
    check_in_date: date
    check_out_date: date


class SearchResponse(BaseModel):
    id: int
    campground_id: int
    site_type: Optional[str]
    check_in_date: date
    check_out_date: date
    status: str

    class Config:
        from_attributes = True


class AvailabilityResponse(BaseModel):
    id: int
    site_id: Optional[str]
    site_name: Optional[str]
    date: Optional[date]
    available: Optional[bool]

    class Config:
        from_attributes = True


@router.get("/", response_model=list[SearchResponse])
def get_searches(db: Session = Depends(get_db)):
    searches = db.query(Search).all()
    return searches


@router.post("/", response_model=SearchResponse)
def create_search(search: SearchCreate, db: Session = Depends(get_db)):
    campground = db.query(Campground).filter(Campground.id == search.campground_id).first()
    if not campground:
        raise HTTPException(status_code=404, detail="Campground not found")

    db_search = Search(
        campground_id=search.campground_id,
        site_type=search.site_type,
        check_in_date=search.check_in_date,
        check_out_date=search.check_out_date
    )
    db.add(db_search)
    db.commit()
    db.refresh(db_search)
    return db_search


@router.delete("/{search_id}")
def delete_search(search_id: int, db: Session = Depends(get_db)):
    search = db.query(Search).filter(Search.id == search_id).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    db.delete(search)
    db.commit()
    return {"message": "Search deleted successfully"}


@router.get("/{search_id}/availability", response_model=list[AvailabilityResponse])
def get_availability(search_id: int, db: Session = Depends(get_db)):
    search = db.query(Search).filter(Search.id == search_id).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    availability = db.query(Availability).filter(Availability.search_id == search_id).all()
    return availability
