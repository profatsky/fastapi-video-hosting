from fastapi import APIRouter

from .auth import router as auth_router
from .comments import router as videos_router

router = APIRouter()
router.include_router(videos_router)
router.include_router(auth_router)
