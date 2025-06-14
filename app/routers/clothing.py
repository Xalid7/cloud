from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Clothing, User
from app.schemas import ClothingCreate, ClothingUpdate, ClothingResponse
from app.auth import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[ClothingResponse])
async def get_clothing_items(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    clothing_items = db.query(Clothing).all()
    return clothing_items

@router.get("/{clothing_id}", response_model=ClothingResponse)
async def get_clothing_item(clothing_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    clothing = db.query(Clothing).filter(Clothing.id == clothing_id).first()
    if not clothing:
        raise HTTPException(status_code=404, detail="Clothing item not found")
    return clothing

@router.post("/", response_model=ClothingResponse)
async def create_clothing_item(
    clothing: ClothingCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    db_clothing = Clothing(**clothing.dict())
    db.add(db_clothing)
    db.commit()
    db.refresh(db_clothing)
    return db_clothing

@router.put("/{clothing_id}", response_model=ClothingResponse)
async def update_clothing_item(
    clothing_id: int, 
    clothing_update: ClothingUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    db_clothing = db.query(Clothing).filter(Clothing.id == clothing_id).first()
    if not db_clothing:
        raise HTTPException(status_code=404, detail="Clothing item not found")
    
    update_data = clothing_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_clothing, field, value)
    
    db.commit()
    db.refresh(db_clothing)
    return db_clothing

@router.delete("/{clothing_id}")
async def delete_clothing_item(
    clothing_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    db_clothing = db.query(Clothing).filter(Clothing.id == clothing_id).first()
    if not db_clothing:
        raise HTTPException(status_code=404, detail="Clothing item not found")
    
    db.delete(db_clothing)
    db.commit()
    return {"message": "Clothing item deleted successfully"}

@router.get("/low-stock/alerts")
async def get_low_stock_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    low_stock_items = db.query(Clothing).filter(Clothing.quantity <= Clothing.minimum_quantity).all()
    return {
        "count": len(low_stock_items),
        "items": low_stock_items
    }
