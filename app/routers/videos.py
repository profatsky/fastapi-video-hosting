from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse

from app.schemas.auth import UserSchema
from app.schemas.videos import VideoCreateSchema, VideoSchema
from app.services.auth import get_current_user
from app.services.videos import VideoService


router = APIRouter(
    prefix="/videos",
    tags=["video"]
)


@router.post("/upload", response_model=VideoSchema)
async def upload_video(
        background_tasks: BackgroundTasks,
        title: str = Form(...),
        description: str = Form(...),
        file: UploadFile = File(...),
        service: VideoService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    if file.content_type != "video/mp4":
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    video_data = VideoCreateSchema(title=title, description=description, author=user)
    return await service.create(background_tasks, file, video_data)


@router.get("/{video_id}", response_model=VideoSchema)
async def get_video(
        video_id: int,
        service: VideoService = Depends()
):
    video = await service.get(video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    file = open(video.file, mode="rb")
    return StreamingResponse(file, media_type="video/mp4")
