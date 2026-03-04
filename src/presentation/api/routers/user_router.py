from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.user_service import UserService
from src.presentation.api.deps import get_user_service
from src.presentation.api.deps import get_session
from src.presentation.schemas.user_schema import UserSchema

user_router = APIRouter(prefix="/users", tags=["user"])

@user_router.post(
    "",
    summary="Create a new user",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
        user: UserSchema = Body(...),
        session: AsyncSession = Depends(get_session),
        user_service: UserService = Depends(get_user_service),
) -> dict:
    return await user_service.create_user(
        session=session,
        user=user,
    )
