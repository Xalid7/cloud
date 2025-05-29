from sqlalchemy import Column, Integer, String, Float, Date
from app.database import Base
from sqlalchemy.orm import relationship

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity_grams = Column(Float, nullable=False)
    unit = Column(String, default="g")
    delivered_at = Column(Date)

    serves = relationship("Serve", back_populates="ingredient")
