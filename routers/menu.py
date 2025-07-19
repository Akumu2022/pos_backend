from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth.dependencies import is_admin

router = APIRouter()

# ------------------ Admin: Create Menu Item ------------------
@router.post("/", response_model=schemas.MenuItemOut)
def create_menu_item(item: schemas.MenuItemCreate, db: Session = Depends(get_db), admin: models.User = Depends(is_admin)):
    db_item = models.MenuItem(**item.dict(),is_active=True)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# ------------------ Admin: List Menu Items ------------------
@router.get("/", response_model=List[schemas.MenuItemOut])
def list_menu_items(db: Session = Depends(get_db), admin: models.User = Depends(is_admin)):
    return db.query(models.MenuItem).filter(models.MenuItem.is_active==True).all()

# everyone can view menu
@router.get("/public", response_model=List[schemas.MenuItemOut])
def get_active_menu_items(category: str = None, db: Session = Depends(get_db)):
    query = db.query(models.MenuItem)  # Remove the is_active filter
    if category:
        query = query.filter(models.MenuItem.category == category)
    return query.all()

# ------------------ Admin: Update Menu Item ------------------
@router.put("/{item_id}", response_model=schemas.MenuItemOut)
def update_menu_item(item_id: int, updates: schemas.MenuItemCreate, db: Session = Depends(get_db), admin: models.User = Depends(is_admin)):
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item

# ------------------ Admin: Soft Delete Menu Item ------------------
@router.delete("/{item_id}")
def soft_delete_menu_item(item_id: int, db: Session = Depends(get_db), admin: models.User = Depends(is_admin)):
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.is_active = False
    db.commit()
    return {"detail": f"Item '{item.name}' has been deactivated"}


# ------------------ Admin: Permanently Delete Menu Item ------------------
@router.delete("/{item_id}")
def permanently_delete_menu_item(item_id: int, db: Session = Depends(get_db), admin: models.User = Depends(is_admin)):
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"detail": f"Item '{item.name}' has been permanently deleted"}
