from fastapi import APIRouter

from .auth import router as auth_router
from .videos import router as videos_router
from .comments import router as comments_router
from .users import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(videos_router)
router.include_router(comments_router)
router.include_router(users_router)
