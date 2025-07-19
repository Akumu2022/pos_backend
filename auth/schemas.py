from pydantic import BaseModel
from datetime import datetime

class UserInfo(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    class Config:
        orm_mode = True

class LoginResponse(BaseModel):
    token: str
    role: str
    user: UserInfo  # ✅ Embed full user object

class LoginRequest(BaseModel):
    username: str
    password: str