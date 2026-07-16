from backend.DB.models import RefreshToken
from sqlalchemy import select

from backend.utils.repository import SQLAlchemyRepository



class JWTRepository(SQLAlchemyRepository):
    model  = RefreshToken
    async def get_one(self, hashed_refresh_token:str):
        stmt = select(self.model).where(
              self.model.token_hash == hashed_refresh_token,
            self.model.revoked == False
        )
        token = await self.session.execute(stmt)
        return token.scalar_one_or_none()

    async def make_revoke_true(self,token_db):
        token_db.revoked = True
        await self.session.commit()
        await self.session.refresh(token_db)

    async def delete_one(self, token_db):
        await self.session.delete(token_db)
        await self.session.commit()