from sqlalchemy import Column, Integer, Date, UniqueConstraint
from app.database import Base
import datetime

class Attendance(Base):
    __tablename__ = "attendances"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=datetime.date.today, unique=True)
    count = Column(Integer, nullable=False)
