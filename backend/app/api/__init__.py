from fastapi import APIRouter
from app.api.upload import router as upload_router
from app.api.chat import router as chat_router

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

router.include_router(upload_router, tags=["upload"])
router.include_router(chat_router, tags=["chat"])
