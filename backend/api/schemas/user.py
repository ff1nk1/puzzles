from pydantic import BaseModel, EmailStr
from sqlalchemy.sql.annotation import Annotated

from backend.DB.database import Base
class User(BaseModel):
    username: str
    password: str
class UserRegister(User):
    email: EmailStr