from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text, DECIMAL, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(20), default="seller")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    sales = relationship("Sale", back_populates="user")

class Clothing(Base):
    __tablename__ = "clothing"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    type = Column(String(50), index=True)  # Shirt, Pants, Dress, etc.
    size = Column(String(20))  # S, M, L, XL, etc.
    color = Column(String(50))
    quantity = Column(Integer, default=0)
    unit = Column(String(20), default="dona")
    price = Column(Numeric(10, 2), default=0)
    cost_price = Column(Numeric(10, 2), default=0)
    minimum_quantity = Column(Integer, default=5)
    supplier = Column(String(100))
    delivery_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    order_items = relationship("OrderItem", back_populates="clothing")
    inventory_logs = relationship("InventoryLog", back_populates="clothing")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    customer_name = Column(String(100))
    customer_phone = Column(String(50))
    status = Column(String(20), default="pending")  # pending, completed, cancelled
    is_active = Column(Boolean, default=True)
    total_amount = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    items = relationship("OrderItem", back_populates="order")
    sales = relationship("Sale", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    clothing_id = Column(Integer, ForeignKey("clothing.id"))
    quantity = Column(Integer)
    unit = Column(String(20), default="dona")
    price = Column(Numeric(10, 2), default=0)
    
    order = relationship("Order", back_populates="items")
    clothing = relationship("Clothing", back_populates="order_items")

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    items_sold = Column(Integer)
    total_amount = Column(Numeric(10, 2), default=0)
    payment_method = Column(String(50), default="cash")
    sold_at = Column(DateTime, server_default=func.now())
    notes = Column(Text)
    
    order = relationship("Order", back_populates="sales")
    user = relationship("User", back_populates="sales")
    inventory_logs = relationship("InventoryLog", back_populates="sale")

class InventoryLog(Base):
    __tablename__ = "inventory_log"
    
    id = Column(Integer, primary_key=True, index=True)
    clothing_id = Column(Integer, ForeignKey("clothing.id"))
    sale_id = Column(Integer, ForeignKey("sales.id"))
    quantity_changed = Column(Integer)
    unit = Column(String(20), default="dona")
    change_type = Column(String(20))  # sale, restock, return, adjustment
    changed_at = Column(DateTime, server_default=func.now())
    
    clothing = relationship("Clothing", back_populates="inventory_logs")
    sale = relationship("Sale", back_populates="inventory_logs")

class MonthlyReport(Base):
    __tablename__ = "monthly_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer)
    year = Column(Integer)
    total_items_sold = Column(Integer, default=0)
    total_revenue = Column(Numeric(10, 2), default=0)
    total_profit = Column(Numeric(10, 2), default=0)
    profit_margin = Column(DECIMAL(5,2))
    is_suspicious = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
