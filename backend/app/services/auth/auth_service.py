from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginResponse, UserCreate


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_repository = UserRepository(session)

    async def register_user(self, payload: UserCreate):
        existing_user = await self.user_repository.get_by_email(payload.email)
        if existing_user is not None:
            raise AppException("A user with this email already exists.", status_code=409, error_code="email_exists")

        return await self.user_repository.create(
            email=str(payload.email),
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )

    async def login_user(self, email: str, password: str) -> LoginResponse:
        user = await self.user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AppException("Incorrect email or password.", status_code=401, error_code="invalid_credentials")
        if not user.is_active:
            raise AppException("This user account is inactive.", status_code=403, error_code="inactive_user")

        token = create_access_token(subject=str(user.id))
        return LoginResponse(access_token=token, user=user)

