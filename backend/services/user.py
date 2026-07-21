from datetime import datetime, timezone, timedelta
import jwt

from backend.core.custom_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    WrongPasswordError,
    RefreshTokenNotFoundError,
    RefreshTokenExpiredError,
)
from backend.repositories.user import UserRepository
from backend.api.schemas.user import UserRegister, RefreshTokenToAdd
from backend.services.security import SecurityService, JWTService
from backend.repositories.jwt import JWTRepository


class UserService:
    def __init__(
        self, user_repo: UserRepository, jwt_repo: JWTRepository | None = None
    ):
        self.user_repo = user_repo
        self.jwt_repo = jwt_repo

    async def check_username_and_email(self, username: str, email: str):
        us_email = await self.user_repo.get_one_by_email(email)
        us_username = await self.user_repo.get_one_by_username(username)
        if us_email:
            raise UserAlreadyExistsError("email", us_email)
        if us_username:
            raise UserAlreadyExistsError("username", us_username.username)
        return True

    async def add_user(self, user_to_add: UserRegister):
        user_dict = user_to_add.model_dump()
        user = dict()
        if await self.check_username_and_email(
            user_dict["username"], user_dict["email"]
        ):
            password = user_dict.pop("password")
            user_dict["hashed_password"] = await SecurityService.hash_password(password)
            user = await self.user_repo.add_one(user_dict)
        return user

    async def login(self, user_data):
        user = await self.user_repo.get_one_by_username(user_data.username)
        if not user:
            raise UserNotFoundError(user_data.username)
        if not await SecurityService.verify_password(
            user_data.password, user.hashed_password
        ):
            raise WrongPasswordError()

        jwt_service = JWTService()
        access_token = await jwt_service.create_access_token(
            data={"sub": user.username}
        )
        refresh_token = await jwt_service.create_refresh_token(
            data={"sub": user.username}
        )
        hashed_refresh_token = await jwt_service.hash_refresh_token(refresh_token)
        refresh_expires_at = datetime.now(timezone.utc).replace(
            tzinfo=None
        ) + timedelta(minutes=JWTService.REFRESH_TOKEN_EXP_MINUTES)
        print("SAVED HASH:", hashed_refresh_token)
        schema_obj = RefreshTokenToAdd(
            user_id=user.id,
            token_hash=hashed_refresh_token,
            expires_at=refresh_expires_at,
        )
        await self.jwt_repo.add_one(data=schema_obj.model_dump())
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
        }

    async def refresh(self, refresh_token: str):
        try:
            jwt_service = JWTService()
            payload = await jwt_service.get_refresh_token(refresh_token)
            username = payload.get("sub")
            user_db = await self.user_repo.get_one_by_username(username)
            if not user_db:
                raise UserNotFoundError(username)
            hashed_refresh_token = await jwt_service.hash_refresh_token(refresh_token)
            refresh_token_db = await self.jwt_repo.get_one(hashed_refresh_token)
            print("LOOKUP HASH:", hashed_refresh_token)
            if not refresh_token_db:
                raise RefreshTokenNotFoundError()
            if refresh_token_db.expires_at < datetime.utcnow():
                raise RefreshTokenExpiredError()

            new_access_token = await jwt_service.create_access_token(
                data={"sub": username}
            )
            new_refresh_token = await jwt_service.create_refresh_token(
                data={"sub": username}
            )

            await self.jwt_repo.make_revoke_true(refresh_token_db)
            await self.jwt_repo.delete_one(refresh_token_db)

            new_hashed_refresh_token = await jwt_service.hash_refresh_token(
                new_refresh_token
            )
            schema_obj = RefreshTokenToAdd(
                user_id=user_db.id,
                token_hash=new_hashed_refresh_token,
                expires_at=datetime.now()
                + timedelta(minutes=JWTService.REFRESH_TOKEN_EXP_MINUTES),
            )
            await self.jwt_repo.add_one(data=schema_obj.model_dump())
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
            }
        except jwt.ExpiredSignatureError:
            raise RefreshTokenExpiredError()

        except jwt.InvalidTokenError:
            raise RefreshTokenNotFoundError()
