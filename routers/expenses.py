from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from requests import Session
from sqlalchemy import func
from typing import Optional
from database import get_db
from models import Expense
from schemas import ExpenseCreate, ExpenseOut

router = APIRouter()

# --- API Router ---
@router.post("/", response_model=ExpenseOut)
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_exp = Expense(**expense.dict())
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

@router.get("/", response_model=List[ExpenseOut])
def list_expenses(db: Session = Depends(get_db)):
    return db.query(Expense).order_by(Expense.date.desc()).all()

@router.delete("/{expense_id}")
def remove_expense(expense_id: int, db: Session = Depends(get_db)):
    exp = db.query(Expense).filter(Expense.id == expense_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(exp)
    db.commit()
    return {"detail": f"Expense {expense_id} deleted"}



@router.get("/summary")
def get_expense_summary(
    period: Optional[str] = Query(None, description="one of: weekly, monthly"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Expense.category, func.sum(Expense.amount))

    # Handle date filters
    if period == "weekly":
        from_date = datetime.utcnow() - timedelta(days=7)
        query = query.filter(Expense.created_at >= from_date)
    elif period == "monthly":
        from_date = datetime.utcnow() - timedelta(days=30)
        query = query.filter(Expense.created_at >= from_date)
    elif start_date and end_date:
        try:
            from_date = datetime.fromisoformat(start_date)
            to_date = datetime.fromisoformat(end_date)
            query = query.filter(Expense.created_at.between(from_date, to_date))
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}

    query = query.group_by(Expense.category)
    results = query.all()

    total = sum([amount for _, amount in results])
    return {
        "total": total,
        "by_category": {category: amount for category, amount in results}
    }