import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.image_model import ImageModel

class ImageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_image(
            self,
            user_id: uuid.UUID,
            image_size: int,
            name: str,
            description: str,
    ) -> ImageModel:
        image = ImageModel(
            user_id=user_id,
            image_size=image_size,
            name=name,
            description=description,
        )
        self.session.add(image)

        return image

    async def get_images(
            self,
            limit: int,
            offset: int,
    ) -> list[ImageModel]:
        query = (
            select(ImageModel)
            .options(selectinload(ImageModel.user))
            .order_by(ImageModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        images = result.scalars().all()

        return images

    async def get_images_user_id(
            self,
            user_id: uuid.UUID,
    ) -> list[ImageModel]:
        query = (
            select(ImageModel)
            .where(ImageModel.user_id == user_id)
            .order_by(ImageModel.created_at.desc())
        )
        result = await self.session.execute(query)
        images = result.scalars().all()

        return images

    async def delete_image(
            self,
            image_id: uuid.UUID,
            user_id: uuid.UUID,
    ) -> ImageModel | None:
        query = (
            select(ImageModel)
            .where(ImageModel.id == image_id)
            .where(ImageModel.user_id == user_id)
        )
        result = await self.session.execute(query)
        image = result.scalar_one_or_none()

        if image:
            self.session.delete(image)

        return image

    async def update_description(
            self,
            image_id: uuid.UUID,
            user_id: uuid.UUID,
            new_description: str,
    ) -> ImageModel | None:
        query = (
            select(ImageModel)
            .where(ImageModel.id == image_id)
            .where(ImageModel.user_id == user_id)
        )
        result = await self.session.execute(query)
        image = result.scalar_one_or_none()

        if image:
            image.description = new_description

        return image

    async def update_name(
        self,
        image_id: uuid.UUID,
        user_id: uuid.UUID,
        new_name: str,
    ) -> ImageModel | None:
        query = (
            select(ImageModel)
            .where(ImageModel.id == image_id)
            .where(ImageModel.user_id == user_id)
        )
        result = await self.session.execute(query)
        image = result.scalar_one_or_none()

        if image:
            image.name = new_name

        return image
