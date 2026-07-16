from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class User(BaseModel):
    username: str
class UserRegister(User):
    password: str
    email: EmailStr

class UserResponse(User):
    id:int

class RefreshTokenToAdd(BaseModel):
    user_id: int
    token_hash: str
    expires_at: datetime