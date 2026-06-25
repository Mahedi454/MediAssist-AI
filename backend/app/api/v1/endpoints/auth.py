from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.auth import LoginResponse, LogoutResponse, UserCreate, UserRead
from app.services.auth.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserRead:
    return await AuthService(session).register_user(payload)


@router.post("/login", response_model=LoginResponse)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    return await AuthService(session).login_user(form_data.username, form_data.password)


@router.post("/logout", response_model=LogoutResponse)
async def logout_user(_current_user: Annotated[User, Depends(get_current_user)]) -> LogoutResponse:
    return LogoutResponse(message="Logged out successfully. Please discard the access token on the client.")


@router.get("/me", response_model=UserRead)
async def get_profile(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user

