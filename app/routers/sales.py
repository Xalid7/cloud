from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Sale, Order, Clothing, OrderItem, InventoryLog, User
from app.schemas import SaleCreate, SaleResponse
from app.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=SaleResponse)
async def create_sale(
    sale: SaleCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Get order and check if it exists
    order = db.query(Order).filter(Order.id == sale.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if order is already completed
    if order.status == "completed":
        raise HTTPException(status_code=400, detail="Order is already completed")
    
    # Check if enough inventory is available
    for item in order.items:
        clothing = db.query(Clothing).filter(Clothing.id == item.clothing_id).first()
        if not clothing:
            raise HTTPException(status_code=400, detail=f"Clothing item not found")
        
        if clothing.quantity < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough {clothing.name} in stock. Required: {item.quantity}, Available: {clothing.quantity}"
            )
    
    # Create sale record
    db_sale = Sale(
        order_id=sale.order_id,
        user_id=current_user.id,
        items_sold=sale.items_sold,
        total_amount=sale.total_amount,
        payment_method=sale.payment_method,
        notes=sale.notes
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    
    # Update order status
    order.status = "completed"
    
    # Deduct items from inventory and log changes
    for item in order.items:
        clothing = db.query(Clothing).filter(Clothing.id == item.clothing_id).first()
        clothing.quantity -= item.quantity
        
        # Log inventory change
        inventory_log = InventoryLog(
            clothing_id=clothing.id,
            sale_id=db_sale.id,
            quantity_changed=-item.quantity,  # Negative for sales
            unit=item.unit,
            change_type="sale"
        )
        db.add(inventory_log)
    
    db.commit()
    
    # Return sale with order and user info
    return {
        "id": db_sale.id,
        "order_id": db_sale.order_id,
        "order_name": order.name,
        "user_id": db_sale.user_id,
        "username": current_user.username,
        "items_sold": db_sale.items_sold,
        "total_amount": float(db_sale.total_amount),
        "payment_method": db_sale.payment_method,
        "sold_at": db_sale.sold_at,
        "notes": db_sale.notes
    }

@router.get("/", response_model=List[SaleResponse])
async def get_sales(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sales = db.query(Sale).order_by(Sale.sold_at.desc()).limit(100).all()
    result = []
    
    for sale in sales:
        order = db.query(Order).filter(Order.id == sale.order_id).first()
        user = db.query(User).filter(User.id == sale.user_id).first()
        
        result.append({
            "id": sale.id,
            "order_id": sale.order_id,
            "order_name": order.name if order else "Unknown",
            "user_id": sale.user_id,
            "username": user.username if user else "Unknown",
            "items_sold": sale.items_sold,
            "total_amount": float(sale.total_amount),
            "payment_method": sale.payment_method,
            "sold_at": sale.sold_at,
            "notes": sale.notes
        })
    
    return result

@router.get("/today", response_model=List[SaleResponse])
async def get_today_sales(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from datetime import date
    today = date.today()
    
    sales = db.query(Sale).filter(
        Sale.sold_at >= today
    ).order_by(Sale.sold_at.desc()).all()
    
    result = []
    for sale in sales:
        order = db.query(Order).filter(Order.id == sale.order_id).first()
        user = db.query(User).filter(User.id == sale.user_id).first()
        
        result.append({
            "id": sale.id,
            "order_id": sale.order_id,
            "order_name": order.name if order else "Unknown",
            "user_id": sale.user_id,
            "username": user.username if user else "Unknown",
            "items_sold": sale.items_sold,
            "total_amount": float(sale.total_amount),
            "payment_method": sale.payment_method,
            "sold_at": sale.sold_at,
            "notes": sale.notes
        })
    
    return result
