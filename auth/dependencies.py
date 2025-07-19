from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
from auth.auth import active_tokens

def get_current_user(token: str = Header(...), db: Session = Depends(get_db)) -> models.User:
    user_id = active_tokens.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return user

def is_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ✅ Add this alias for clarity and import compatibility
get_current_admin = is_admin
