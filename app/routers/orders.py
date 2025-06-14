from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, OrderItem, Clothing, User
from app.schemas import OrderCreate, OrderUpdate, OrderResponse, OrderItemResponse
from app.auth import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[OrderResponse])
async def get_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.is_active == True).all()
    result = []
    
    for order in orders:
        order_dict = {
            "id": order.id,
            "name": order.name,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "status": order.status,
            "is_active": order.is_active,
            "total_amount": float(order.total_amount),
            "created_at": order.created_at,
            "items": []
        }
        
        for item in order.items:
            clothing = db.query(Clothing).filter(Clothing.id == item.clothing_id).first()
            order_dict["items"].append({
                "id": item.id,
                "clothing_id": item.clothing_id,
                "quantity": item.quantity,
                "unit": item.unit,
                "price": float(item.price),
                "clothing_name": clothing.name if clothing else "Unknown"
            })
        
        result.append(order_dict)
    
    return result

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_dict = {
        "id": order.id,
        "name": order.name,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "status": order.status,
        "is_active": order.is_active,
        "total_amount": float(order.total_amount),
        "created_at": order.created_at,
        "items": []
    }
    
    for item in order.items:
        clothing = db.query(Clothing).filter(Clothing.id == item.clothing_id).first()
        order_dict["items"].append({
            "id": item.id,
            "clothing_id": item.clothing_id,
            "quantity": item.quantity,
            "unit": item.unit,
            "price": float(item.price),
            "clothing_name": clothing.name if clothing else "Unknown"
        })
    
    return order_dict

@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin", "manager", "seller"]))
):
    # Calculate total amount
    total_amount = 0
    for item in order.items:
        clothing = db.query(Clothing).filter(Clothing.id == item.clothing_id).first()
        if not clothing:
            raise HTTPException(status_code=404, detail=f"Clothing item with ID {item.clothing_id} not found")
        total_amount += item.price * item.quantity
    
    # Create order
    db_order = Order(
        name=order.name,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        status=order.status,
        total_amount=total_amount
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Add items
    for item in order.items:
        db_item = OrderItem(
            order_id=db_order.id,
            clothing_id=item.clothing_id,
            quantity=item.quantity,
            unit=item.unit,
            price=item.price
        )
        db.add(db_item)
    
    db.commit()
    
    # Return order with items
    return await get_order(db_order.id, db, current_user)

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int, 
    order_update: OrderUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update order basic info
    if order_update.name is not None:
        db_order.name = order_update.name
    if order_update.customer_name is not None:
        db_order.customer_name = order_update.customer_name
    if order_update.customer_phone is not None:
        db_order.customer_phone = order_update.customer_phone
    if order_update.status is not None:
        db_order.status = order_update.status
    if order_update.is_active is not None:
        db_order.is_active = order_update.is_active
    
    # Update items if provided
    if order_update.items is not None:
        # Delete existing items
        db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
        
        # Calculate new total amount
        total_amount = 0
        for item in order_update.items:
            total_amount += item.price * item.quantity
        
        db_order.total_amount = total_amount
        
        # Add new items
        for item in order_update.items:
            db_item = OrderItem(
                order_id=order_id,
                clothing_id=item.clothing_id,
                quantity=item.quantity,
                unit=item.unit,
                price=item.price
            )
            db.add(db_item)
    
    db.commit()
    return await get_order(order_id, db, current_user)

@router.delete("/{order_id}")
async def delete_order(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(db_order)
    db.commit()
    return {"message": "Order deleted successfully"}

@router.get("/pending/list")
async def get_pending_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pending_orders = db.query(Order).filter(Order.status == "pending", Order.is_active == True).all()
    return pending_orders
