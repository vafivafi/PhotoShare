from fastapi import APIRouter, Depends, status, Body, Path
from fastapi.security import HTTPBearer
from authx import TokenPayload
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.user_service import UserService
from src.presentation.api.deps import get_user_service, get_session, get_current_payload
from src.presentation.schemas.user_schema import UserSchema, UpdateUsernameSchema

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

@user_router.post(
    "/login",
    summary="Login a user",
    status_code=status.HTTP_200_OK,
)
async def login(
        user: UserSchema = Body(...),
        session: AsyncSession = Depends(get_session),
        user_service: UserService = Depends(get_user_service),
):
    return await user_service.login(
        session=session,
        user=user,
    )

@user_router.get(
    "/{username}",
    summary="Get a user",
    status_code=status.HTTP_200_OK,
)
async def get_user(
        username: str = Path(
            min_length=3,
            max_length=25,
            description="The username to look up",
            examples="username",
        ),
        session: AsyncSession = Depends(get_session),
        user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user(
        username=username,
        session=session,
    )

@user_router.get(
    "/{username}/images",
    summary="Get a user's images",
    status_code=status.HTTP_200_OK,
)
async def get_by_username_with_images(
        username: str = Path(
            min_length=3,
            max_length=25,
            description="The username to look up the images",
            examples="username",
        ),
        session: AsyncSession = Depends(get_session),
        user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_by_username_with_images(
        session=session,
        username=username,
    )

@user_router.get(
    "/me/profile",
    summary="User profile",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(HTTPBearer())]
)
async def profile(
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
    payload: TokenPayload = Depends(get_current_payload)
):
    return await user_service.profile(
        session=session,
        payload=payload,
    )

@user_router.post(
    "/me/update-username",
    summary="Update username",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(HTTPBearer())]
)
async def update_username(
    username: UpdateUsernameSchema = Body(...),
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
    payload: TokenPayload = Depends(get_current_payload),
):
    return await user_service.update_username(
        session=session,
        payload=payload,
        username=username,
    )
