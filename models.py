from sqlalchemy import Column, text, Date, Integer, String, Float, DateTime, ForeignKey, Boolean, func, Enum as SqlEnum
from sqlalchemy.orm import relationship, declarative_base
from datetime import date
from enum import Enum 

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(255))
    role = Column(String(10), server_default=text("'user'"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    is_active = Column(Boolean, server_default=text("1"))

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Float)
    stock_quantity = Column(Integer, nullable=True)
    category = Column(String(50), nullable=True)
    is_active = Column(Boolean, server_default=text("1"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float, server_default=text("0"))
    order_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    status = Column(String(20), server_default=text("'pending'"))
    is_active = Column(Boolean, server_default=text("1"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)
    unit_price = Column(Float)
    subtotal = Column(Float)
    order = relationship("Order", back_populates="items")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

# ***************************

class AssetStatus(Enum):
    working = "working"
    repair = "repair"
    dispose = "dispose"

class Asset(Base):
    __tablename__ = "assets"  
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    quantity = Column(Integer, server_default=text("1"))
    value = Column(Float, nullable=True)
    purchase_date = Column(Date, default=date.today)  # keep Python default for static value
    status = Column(String(50), server_default=text("'working'"))
    added_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
