import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.user_model import UserModel

class UserRepository:
    async def create(
            self,
            session: AsyncSession,
            username: str,
            hashed_password: str,
    ) -> UserModel:

        user = UserModel(
            username=username,
            password=hashed_password,
        )
        session.add(user)
        return user

    async def get_by_username(
            self,
            username: str,
            session: AsyncSession,
    ) -> UserModel | None:
        query = select(UserModel).where(UserModel.username == username)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username_with_images(
            self,
            session: AsyncSession,
            username: str,
    ) -> UserModel | None:
        query = (
            select(UserModel)
            .where(UserModel.username == username)
            .options(selectinload(UserModel.images))
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def update_username(
            self,
            session: AsyncSession,
            user_id: uuid.UUID,
            new_username: str,
    ) -> UserModel | None:

        query = (
            select(UserModel)
            .where(UserModel.id == user_id)
        )

        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            user.username = new_username

        return user

    async def get_by_id(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
    ) -> UserModel | None:

        query = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(selectinload(UserModel.images))
        )
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        return user
