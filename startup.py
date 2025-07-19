from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from utils import hash_password
from datetime import datetime

def initialize_admin():
    db: Session = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            admin_user = User(
                username="admin",
                password_hash=hash_password("admin"),
                role="admin",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()
