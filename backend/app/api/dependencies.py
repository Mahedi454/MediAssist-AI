from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if subject is None:
            raise AppException("Invalid authentication token.", status_code=401, error_code="invalid_token")
        user_id = int(subject)
    except (JWTError, ValueError):
        raise AppException("Invalid authentication token.", status_code=401, error_code="invalid_token") from None

    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise AppException("User not found or inactive.", status_code=401, error_code="inactive_user")
    return user

