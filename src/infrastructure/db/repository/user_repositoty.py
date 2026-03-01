from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.log.logger import logger
from src.infrastructure.db.models.user_model import UserModel

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
            self,
            username: str,
            hashed_password: str,
    ) -> UserModel:

        user = UserModel(
            username=username,
            password=hashed_password,
        )
        self.session.add(user)
        return user

    async def get_by_username(self, username: str) -> UserModel | None:
        query = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username_with_images(
            self,
            username: str,
    ) -> UserModel | None:
        query = (
            select(UserModel)
            .where(UserModel.username == username)
            .options(selectinload(UserModel.images))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
