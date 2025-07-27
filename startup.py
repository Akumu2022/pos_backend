from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from auth.auth import get_password_hash
from datetime import datetime

def initialize_admin():
    db: Session = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            admin_user = User(
                username="admin",
                password_hash=get_password_hash("admin"),
                role="admin",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin user created successfully")
        else:
            print("✅ Admin user already exists")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
    finally:
        db.close()
