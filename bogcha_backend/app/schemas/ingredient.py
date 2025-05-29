
from pydantic import BaseModel
from datetime import date
from typing import Optional

class IngredientBase(BaseModel):
    name: str
    quantity_grams: float  # ✅ majburiy!
    delivered_at: Optional[date] = None  # ✅ optional

class IngredientOut(BaseModel):
    id: int
    name: str
    quantity_grams: float
    delivered_at: Optional[date]

    class Config:
        orm_mode = True


class IngredientCreate(BaseModel):
    name: str
    quantity_grams: float  # ← nom to‘g‘ri bo‘lishi shart!
    delivered_at: Optional[date] = None

class IngredientUpdate(IngredientBase):
    pass

class IngredientInDB(IngredientBase):
    id: int

    class Config:
        orm_mode = True
