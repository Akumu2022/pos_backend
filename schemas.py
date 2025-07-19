from enum import Enum
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import date, datetime

# ------------------ User ------------------
class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str]="staff"

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: Optional[str]
    password: Optional[str]


# ------------------ Menu ------------------
class MenuItemCreate(BaseModel):
    name: str
    price: float
    stock_quantity: Optional[int] = 1
    category: Optional[str] = "Uncategorized"

class MenuItemOut(BaseModel):
    id: int
    name: str
    price: float
    stock_quantity: Optional[int] = 1
    category: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


# ------------------ Orders ------------------
class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: Optional[int] = 1

class UserOrderCreate(BaseModel):  # 👈 for /user order endpoint
    items: List[OrderItemCreate]

class OrderCreate(BaseModel):  # for admin order creation
    user_id: int
    items: List[OrderItemCreate]

class OrderItemOut(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        orm_mode = True

class OrderOut(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    order_date: datetime
    items: List[OrderItemOut]

    class Config:
        orm_mode = True

class OrderReceipt(BaseModel):  # 👈 for /user order receipt response
    order_id: int
    items: List[dict]
    total_amount: float
    served_by: str
    served_at: str

class ItemStats(BaseModel):
    name: str
    quantity: int

class SalesInsights(BaseModel):
    busiest_day: Optional[str]
    busiest_hour: Optional[str]
    top_selling_item: Optional[dict]
    poor_selling_item: Optional[dict]
    best_performing_staff: Optional[dict]
    poor_performing_staff: Optional[dict]
    highest_sales_day: Optional[dict]
    lowest_sales_day: Optional[dict]
    highest_order_amount: Optional[float]
    lowest_order_amount: Optional[float]


# Expense Schemas (Pydantic)
from pydantic import BaseModel
from typing import Optional
from datetime import date

class ExpenseBase(BaseModel):
    category: str
    amount: float
    description: Optional[str] = None
    date: Optional[date]  # ✅ Accepts actual date values or None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseOut(ExpenseBase):
    id: int
    date: Optional[date]  # ✅ Ensure this explicitly allows returning date

    class Config:
        orm_mode = True

# schemas for asset
class AssetStatus(str, Enum):  # Use `str` to allow JSON serialization
    working = "working"
    repair = "repair"
    dispose = "dispose"

# ✅ Base schema for creation (POST)
class AssetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int = 1
    value: Optional[float] = None
    purchase_date: Optional[date] = None
    status: AssetStatus = AssetStatus.working

# ✅ For reading an asset (GET)
class AssetOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    quantity: int
    value: Optional[float]
    purchase_date: Optional[date]
    status: AssetStatus
    added_at: datetime  # Changed from created_at to match your model
    updated_at: Optional[datetime] = None  # Make optional since it might be None
    
    class Config:
        from_attributes = True  # Updated for Pydantic v2

