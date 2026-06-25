from fastapi import APIRouter

from app.api.v1.endpoints import auth, health

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(health.router, prefix="/health", tags=["Health"])
