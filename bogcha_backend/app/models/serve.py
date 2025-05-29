from sqlalchemy import Column, Integer, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Serve(Base):
    __tablename__ = "serves"

    id = Column(Integer, primary_key=True, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"))
    amount_used = Column(Float, nullable=False)
    served_at = Column(Date, nullable=False)

    ingredient = relationship("Ingredient", back_populates="serves")
