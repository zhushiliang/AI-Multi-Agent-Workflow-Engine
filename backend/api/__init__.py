from fastapi import APIRouter
from .chat import router as chat_router
from .workflows import router as workflows_router

router = APIRouter()
router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(workflows_router, prefix="/workflows", tags=["workflows"])
