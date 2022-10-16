from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.schemas.auth import UserSchema
from app.schemas.videos import VideoCreateSchema, VideoSchema
from app.services.auth import get_current_user
from app.services.videos import VideoService


templates = Jinja2Templates(directory="app/templates")

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


@router.get("/{video_id}", response_class=HTMLResponse)
async def get_video(
        request: Request,
        video_id: int,
        service: VideoService = Depends()
):
    video = await service.get(video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse(
        "videos.html", {"request": request, "video_data": video}
    )


@router.get("/watch/{video_id}")
async def get_streaming_video(
        video_id: int,
        request: Request,
        service: VideoService = Depends()
) -> StreamingResponse:
    file, status_code, content_length, headers = await service.open_file(request, video_id)
    response = StreamingResponse(
        file,
        media_type="video/mp4",
        status_code=status_code
    )

    response.headers.update({
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        **headers
    })
    return response
