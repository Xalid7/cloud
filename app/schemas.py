from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "seller"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Clothing schemas
class ClothingBase(BaseModel):
    name: str
    type: str
    size: str
    color: str
    quantity: int
    unit: str = "dona"
    price: float
    cost_price: float
    minimum_quantity: int = 5
    supplier: Optional[str] = None
    delivery_date: Optional[date] = None

class ClothingCreate(ClothingBase):
    pass

class ClothingUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    minimum_quantity: Optional[int] = None
    supplier: Optional[str] = None
    delivery_date: Optional[date] = None

class ClothingResponse(ClothingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Order schemas
class OrderItemBase(BaseModel):
    clothing_id: int
    quantity: int
    unit: str = "dona"
    price: float

class OrderItemResponse(OrderItemBase):
    id: int
    clothing_name: str
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    name: str
    customer_name: str
    customer_phone: str
    status: str = "pending"

class OrderCreate(OrderBase):
    items: List[OrderItemBase]

class OrderUpdate(BaseModel):
    name: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    items: Optional[List[OrderItemBase]] = None

class OrderResponse(OrderBase):
    id: int
    is_active: bool
    total_amount: float
    created_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True

# Sale schemas
class SaleCreate(BaseModel):
    order_id: int
    items_sold: int
    total_amount: float
    payment_method: str = "cash"
    notes: Optional[str] = None

class SaleResponse(BaseModel):
    id: int
    order_id: int
    order_name: str
    user_id: int
    username: str
    items_sold: int
    total_amount: float
    payment_method: str
    sold_at: datetime
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

# Report schemas
class MonthlyReportResponse(BaseModel):
    id: int
    month: int
    year: int
    total_items_sold: int
    total_revenue: float
    total_profit: float
    profit_margin: float
    is_suspicious: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str
