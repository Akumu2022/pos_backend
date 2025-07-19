from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from auth.schemas import LoginRequest, LoginResponse
from auth.auth import authenticate_user, create_session_token
from database import get_db

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(data.username, data.password, db)
    token = create_session_token(user.id)

    return {
        "token": token,
        "role": user.role,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "created_at": user.created_at
        }
    }

