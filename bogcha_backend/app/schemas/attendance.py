from pydantic import BaseModel
from datetime import date

class AttendanceBase(BaseModel):
    date: date
    count: int

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceOut(AttendanceBase):
    id: int

    class Config:
        orm_mode = True
