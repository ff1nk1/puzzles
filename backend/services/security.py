from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta
from typing import Dict
import jwt
import os
from fastapi.security import OAuth2PasswordBearer
import hashlib

from backend.core.custom_exceptions import (
    RefreshTokenNotFoundError,
    RefreshTokenExpiredError,
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
SECRET_KEY = os.getenv("SECRET_KEY")
pwd_context = PasswordHash.recommended()


class SecurityService:
    @staticmethod
    async def hash_password(password: str):
        return pwd_context.hash(password)

    @staticmethod
    async def verify_password(input_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(input_password, hashed_password)


class JWTService:
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXP_MINUTES = 228

    async def get_jwt_token(self, token):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[self.ALGORITHM])
        return payload

    async def create_access_token(self, data: Dict):
        to_encode = data.copy()
        expire_time = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
            minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire_time})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=self.ALGORITHM)

    async def create_refresh_token(self, data: Dict):
        to_encode = data.copy()
        expire_time = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
            minutes=self.REFRESH_TOKEN_EXP_MINUTES
        )
        to_encode.update({"exp": expire_time, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=self.ALGORITHM)

    async def get_refresh_token(self, refresh_token: str):
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[self.ALGORITHM])
        if payload.get("type", None) != "refresh":
            raise RefreshTokenNotFoundError()
        return payload

    @staticmethod
    async def check_refresh_token(token):
        if not token:
            raise RefreshTokenNotFoundError()
        if token.expires_at < datetime.utcnow():
            raise RefreshTokenExpiredError()

    @staticmethod
    async def hash_refresh_token(token: str):
        return hashlib.sha256(token.encode()).hexdigest()
