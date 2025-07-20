from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth.dependencies import get_current_admin 
from auth.auth import get_password_hash

router = APIRouter()

# ------------------ Admin: Create User ------------------
@router.post("/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = models.User(
        username=user.username,
        password_hash=get_password_hash(user.password),
        role=user.role or "staff",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ------------------ Admin: List Users ------------------
@router.get("/", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    return db.query(models.User).all()

# ------------------ Admin: Update User ------------------
@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    updates: schemas.UserUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Check for duplicate username if it's being updated
    if updates.username:
        existing = db.query(models.User).filter(
            models.User.username == updates.username,
            models.User.id != user_id  # Exclude current user
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already in use")
        user.username = updates.username

    # ✅ Update password if provided
    if updates.password:
        user.password_hash = get_password_hash(updates.password)

    db.commit()
    db.refresh(user)
    return user


# ------------------ Admin: Soft Delete User ------------------
@router.delete("/{user_id}")
def soft_delete_user(user_id: int, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()
    return {"detail": f"User {user.username} has been deactivated"}

# ------------------ Admin: Update Their Own Credentials ------------------
@router.put("/me/update", response_model=schemas.UserOut)
def update_own_admin_credentials(updates: schemas.UserUpdate, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    admin.username = updates.username or admin.username
    if updates.password:
        admin.password_hash = get_password_hash(updates.password)
    db.commit()
    db.refresh(admin)
    return admin

# we are trying 
# not to log in
# already deactivated user


@router.patch("/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.commit()
    return {"status": "updated", "is_active": user.is_active}
