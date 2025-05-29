from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# Ingredient'ni chiqishda ko‘rsatish uchun
class IngredientOut(BaseModel):
    id: int
    name: str
    quantity_grams: float

    class Config:
        orm_mode = True


# MealIngredient chiqishda ingredient obyektini ham olib yuradi
class MealIngredientOut(BaseModel):
    ingredient_id: int
    amount_grams: float
    ingredient: IngredientOut  # JOIN natijasi

    class Config:
        orm_mode = True


# Ovqat yaratish uchun kiruvchi model
class MealIngredientIn(BaseModel):
    ingredient_id: int
    amount_grams: float


class MealCreate(BaseModel):
    name: str
    cooked_at: datetime
    ingredients: List[MealIngredientIn]


# Ovqat chiqishda ingredientlar bilan birga
class MealOut(BaseModel):
    id: int
    name: str
    cooked_at: Optional[datetime]
    ingredients: List[MealIngredientOut]

    class Config:
        orm_mode = True
