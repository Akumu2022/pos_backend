import secrets
from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
active_tokens = {}  # token: user_id map (in-memory; can later use Redis/db)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str, db: Session):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been deactivated")

    return user



def create_session_token(user_id: int):
    token = secrets.token_hex(32)
    active_tokens[token] = user_id
    return token
