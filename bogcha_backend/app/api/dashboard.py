from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.portions import get_usage_report, get_delivered_report

router = APIRouter()

@router.get("/reports/usage/")
def usage_report(db: Session = Depends(get_db)):
    return get_usage_report(db)

@router.get("/reports/delivered/")
def delivered_report(db: Session = Depends(get_db)):
    return get_delivered_report(db)
