from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List
from database import get_db
import models, schemas
from auth.dependencies import get_current_admin

router = APIRouter()


# ------------------ ✅ USER: Create Order ------------------
@router.post("/", response_model=schemas.OrderOut)
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    # ✅ Ensure user exists
    user = db.query(models.User).filter(models.User.id == order_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total_amount = 0
    order_items = []

    for item in order_data.items:
        menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item ID {item.menu_item_id} not found.")

        qty = item.quantity or 1  # ✅ Default to 1 if not provided

        # ✅ Optional: Adjust stock if available
        if menu_item.stock_quantity is not None:
            menu_item.stock_quantity = max(0, menu_item.stock_quantity - qty)

        subtotal = menu_item.price * qty
        total_amount += subtotal

        order_items.append(models.OrderItem(
            menu_item_id=item.menu_item_id,
            quantity=qty,
            unit_price=menu_item.price,
            subtotal=subtotal
        ))

    new_order = models.Order(
        user_id=order_data.user_id,
        total_amount=total_amount,
        status="completed",
        order_date=datetime.utcnow(),
        items=order_items
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in new_order.items:
        db.refresh(item)

    return new_order


# ------------------ ✅ ADMIN: List All Orders ------------------
@router.get("/", response_model=List[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    return db.query(models.Order).order_by(models.Order.order_date.desc()).all()

# ------------------ ✅ ADMIN: Update Order Status ------------------
@router.put("/{order_id}")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    return {"detail": f"Order {order_id} status updated to '{status}'"}


# ------------------ ✅ ADMIN: View Order Stats ------------------
@router.get("/stats")
def order_stats(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today.replace(day=1)

    total_today = db.query(func.count(models.Order.id))\
        .filter(func.date(models.Order.order_date) == today).scalar()

    total_week = db.query(func.count(models.Order.id))\
        .filter(models.Order.order_date >= week_ago).scalar()

    total_month = db.query(func.count(models.Order.id))\
        .filter(models.Order.order_date >= month_ago).scalar()

    # ✅ NEW: Total amount sold today
    total_sales_today = db.query(func.sum(models.Order.total_amount))\
        .filter(func.date(models.Order.order_date) == today).scalar() or 0

    return {
        "today": total_today,
        "this_week": total_week,
        "this_month": total_month,
        "total_sales_today": total_sales_today  # ✅ include this in return
    }
