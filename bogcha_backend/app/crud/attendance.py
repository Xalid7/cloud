from sqlalchemy.orm import Session
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate
import datetime

def get_today_attendance(db: Session, date_: datetime.date):
    return db.query(Attendance).filter(Attendance.date == date_).first()

def create_or_update_attendance(db: Session, data: AttendanceCreate) -> Attendance:
    att = db.query(Attendance).filter(Attendance.date == data.date).first()
    if att:
        att.count = data.count
    else:
        att = Attendance(date=data.date, count=data.count)
        db.add(att)
    db.commit()
    db.refresh(att)
    return att
