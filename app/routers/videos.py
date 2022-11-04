from typing import List

from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException, status, BackgroundTasks, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.dependencies.videos import valid_video_id, valid_owned_video
from app.models import VideoModel
from app.schemas.users import UserSchema
from app.schemas.videos import VideoCreateSchema, VideoSchema, VideoUpdateSchema
from app.dependencies.auth import get_current_user
from app.services.videos import VideoService


templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/videos",
    tags=["videos"]
)


@router.post("/upload", response_model=VideoSchema, status_code=status.HTTP_201_CREATED)
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
        video: VideoModel = Depends(valid_video_id)
):
    return templates.TemplateResponse(
        "videos.html", {"request": request, "video_data": video}
    )


@router.get("/{video_id}/watching")
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


@router.patch("/{video_id}", response_model=VideoSchema)
async def update_video(
        video_data: VideoUpdateSchema,
        video: VideoModel = Depends(valid_owned_video),
        service: VideoService = Depends(),
):
    return await service.update(video.id, video_data)


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(

        video: VideoModel = Depends(valid_owned_video),
        service: VideoService = Depends()
):
    await service.delete(video.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{video_od}/likes", response_model=List[UserSchema])
async def get_video_likes(
        video: VideoModel = Depends(valid_video_id)
):
    return video.likes


@router.put("/{video_id}/likes", status_code=status.HTTP_200_OK)
async def like_video(
        user: UserSchema = Depends(get_current_user),
        video: VideoModel = Depends(valid_video_id),
        service: VideoService = Depends()
):
    if user.id in await service.get_like_list(video.id):
        await service.like(video.id, user.id)
    return Response(status_code=status.HTTP_200_OK)


@router.delete("/{video_id}/likes", status_code=status.HTTP_200_OK)
async def unlike_video(
        user: UserSchema = Depends(get_current_user),
        video: VideoModel = Depends(valid_video_id),
        service: VideoService = Depends()
):
    if user.id not in await service.get_like_list(video.id):
        await service.unlike(video.id, user.id)
    return Response(status_code=status.HTTP_200_OK)
