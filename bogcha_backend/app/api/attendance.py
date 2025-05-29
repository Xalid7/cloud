from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.schemas.attendance import AttendanceCreate, AttendanceOut
from app.crud import attendance as crud_attendance

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/", response_model=AttendanceOut)
def create_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    return crud_attendance.create_or_update_attendance(db, data)

@router.get("/today", response_model=Optional[AttendanceOut])
def get_today_attendance(db: Session = Depends(get_db)):
    return crud_attendance.get_today_attendance(db, date.today())
