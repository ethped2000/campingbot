from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from models import Campground
from database import get_db

router = APIRouter(prefix="/api/campgrounds", tags=["campgrounds"])


class CampgroundResponse(BaseModel):
    id: int
    name: str
    park_id: Optional[str]
    region: Optional[str]
    url: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=list[CampgroundResponse])
def get_campgrounds(db: Session = Depends(get_db)):
    campgrounds = db.query(Campground).all()
    return campgrounds
