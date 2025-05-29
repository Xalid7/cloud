from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class MealIngredient(Base):
    __tablename__ = "meal_ingredients"

    meal_id = Column(Integer, ForeignKey("meals.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    amount_grams = Column(Float, nullable=False)

    # Ingredient obyektini bog‘lash (JOIN uchun)
    ingredient = relationship("Ingredient", backref="meal_links")


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    cooked_at = Column(DateTime, default=datetime.utcnow)

    # Many-to-many orqali MealIngredient orqali ingredientlar
    ingredients = relationship(
        "MealIngredient",
        backref="meal",
        cascade="all, delete"
    )
