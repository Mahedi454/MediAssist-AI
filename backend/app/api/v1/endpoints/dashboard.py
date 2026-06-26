from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import DashboardService

router = APIRouter()


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    recent_limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> DashboardResponse:
    return await DashboardService(session).get_overview(current_user, recent_limit)
