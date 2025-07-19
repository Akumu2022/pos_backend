from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from enum import Enum
from typing import Literal, Tuple
from database import get_db
from models import Order, OrderItem, MenuItem, User
from auth.dependencies import get_current_admin

router = APIRouter()

class PeriodEnum(str, Enum):
    weekly = "weekly"
    monthly = "monthly"
    all = "all"

def get_period_range(period: PeriodEnum) -> Tuple[datetime, datetime]:
    today = datetime.now()
    if period == PeriodEnum.weekly:
        start = today - timedelta(days=7)
    elif period == PeriodEnum.monthly:
        start = today - timedelta(days=30)
    else:  # PeriodEnum.all
        start = datetime(2000, 1, 1)
    return start, today

@router.get("/insights")
def sales_insights(
    period: PeriodEnum = Query(PeriodEnum.weekly, description="weekly | monthly | all"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    print("Period received: ", period)
    start_date, end_date = get_period_range(period)

    busiest_day = db.query(func.date(Order.order_date), func.count(Order.id))\
        .filter(Order.order_date >= start_date)\
        .group_by(func.date(Order.order_date))\
        .order_by(func.count(Order.id).desc())\
        .first()

    busiest_hour = db.query(func.concat(func.hour(Order.order_date), ':00'), func.count(Order.id))\
        .filter(Order.order_date >= start_date)\
        .group_by(func.hour(Order.order_date))\
        .order_by(func.count(Order.id).desc())\
        .first()

    top_item = db.query(MenuItem.name, func.sum(OrderItem.quantity))\
        .join(MenuItem, MenuItem.id == OrderItem.menu_item_id)\
        .join(Order, Order.id == OrderItem.order_id)\
        .filter(Order.order_date >= start_date)\
        .group_by(MenuItem.name)\
        .order_by(func.sum(OrderItem.quantity).desc())\
        .first()

    poor_item = db.query(MenuItem.name, func.sum(OrderItem.quantity))\
        .join(MenuItem, MenuItem.id == OrderItem.menu_item_id)\
        .join(Order, Order.id == OrderItem.order_id)\
        .filter(Order.order_date >= start_date)\
        .group_by(MenuItem.name)\
        .order_by(func.sum(OrderItem.quantity).asc())\
        .first()

    best_staff = db.query(User.username, func.sum(Order.total_amount))\
        .join(User, User.id == Order.user_id)\
        .filter(Order.order_date >= start_date)\
        .group_by(User.username)\
        .order_by(func.sum(Order.total_amount).desc())\
        .first()

    poor_staff = db.query(User.username, func.sum(Order.total_amount))\
        .join(User, User.id == Order.user_id)\
        .filter(User.username != "admin", Order.order_date >= start_date)\
        .group_by(User.username)\
        .order_by(func.sum(Order.total_amount).asc())\
        .first()

    highest_day = db.query(func.date(Order.order_date), func.sum(Order.total_amount))\
        .filter(Order.order_date >= start_date)\
        .group_by(func.date(Order.order_date))\
        .order_by(func.sum(Order.total_amount).desc())\
        .first()

    lowest_day = db.query(func.date(Order.order_date), func.sum(Order.total_amount))\
        .filter(Order.order_date >= start_date)\
        .group_by(func.date(Order.order_date))\
        .order_by(func.sum(Order.total_amount).asc())\
        .first()

    highest_order = db.query(func.max(Order.total_amount))\
        .filter(Order.order_date >= start_date)\
        .scalar()

    lowest_order = db.query(func.min(Order.total_amount))\
        .filter(Order.order_date >= start_date)\
        .scalar()

    return {
        "period": period.value,
        "busiest_day": busiest_day[0].isoformat() if busiest_day else None,
        "busiest_hour": busiest_hour[0] if busiest_hour else None,
        "top_selling_item": {
            "name": top_item[0],
            "quantity": int(top_item[1])
        } if top_item else None,
        "poor_selling_item": {
            "name": poor_item[0],
            "quantity": int(poor_item[1])
        } if poor_item else None,
        "best_performing_staff": {
            "username": best_staff[0],
            "total_sales": float(best_staff[1])
        } if best_staff else None,
        "poor_performing_staff": {
            "username": poor_staff[0],
            "total_sales": float(poor_staff[1])
        } if poor_staff else None,
        "highest_sales_day": {
            "date": highest_day[0].isoformat(),
            "total": float(highest_day[1])
        } if highest_day else None,
        "lowest_sales_day": {
            "date": lowest_day[0].isoformat(),
            "total": float(lowest_day[1])
        } if lowest_day else None,
        "highest_order_amount": float(highest_order) if highest_order else 0,
        "lowest_order_amount": float(lowest_order) if lowest_order else 0
    }

@router.get("/chart-data")
def chart_data(
    period: Literal["weekly", "monthly", "all"] = Query("weekly"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    print("Received chart period:", period, type(period))  # 🐞 Debug log
    start_date, end_date = get_period_range(PeriodEnum(period))  # ✅ safely cast to Enum

    results = db.query(
        func.date(Order.order_date).label("day"),
        func.sum(Order.total_amount).label("total")
    ).filter(Order.order_date >= start_date)\
     .group_by(func.date(Order.order_date))\
     .order_by(func.date(Order.order_date))\
     .all()

    chart = [{"date": row.day.isoformat(), "total": float(row.total)} for row in results]

    return {
        "period": period,  # ✅ No `.value` here, it's already a string
        "chart_data": chart
    }

