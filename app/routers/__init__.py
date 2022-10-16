from fastapi import APIRouter

from .videos import router as videos_router
from .auth import router as auth_router

router = APIRouter()
router.include_router(videos_router)
router.include_router(auth_router)
