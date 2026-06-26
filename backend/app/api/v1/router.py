from fastapi import APIRouter

from app.api.v1.endpoints import auth, chat, dashboard, documents, health, rag

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(chat.router, prefix="/chat", tags=["Chat"])
router.include_router(documents.router, prefix="/documents", tags=["Documents"])
router.include_router(rag.router, prefix="/rag", tags=["Document Q&A"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(health.router, prefix="/health", tags=["Health"])
