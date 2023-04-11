from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .auth.routers import router as auth_router
from .comments.routers import router as comments_router
from .users.routers import router as users_router
from .videos.routers import router as videos_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(comments_router)
router.include_router(users_router)
router.include_router(videos_router)

app = FastAPI(
    title="Video hosting"
)

app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
