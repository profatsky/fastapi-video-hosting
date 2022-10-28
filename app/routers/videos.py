from typing import List

from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException, status, BackgroundTasks, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.schemas.users import UserSchema
from app.schemas.videos import VideoCreateSchema, VideoSchema, VideoUpdateSchema
from app.services.auth import get_current_user
from app.services.videos import VideoService


templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/videos",
    tags=["videos"]
)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
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
    await service.create(background_tasks, file, video_data)
    return Response(status_code=status.HTTP_201_CREATED)


@router.get("/{video_id}", response_class=HTMLResponse)
async def get_video(
        request: Request,
        video_id: int,
        service: VideoService = Depends()
):
    video = await service.get(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video doesn't exist"
        )

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


@router.put("/{video_id}", response_model=VideoSchema)
async def update_video(
        video_id: int,
        video_data: VideoUpdateSchema,
        service: VideoService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    video = await service.get(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video doesn't exist"
        )
    if video.author.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have permission"
        )

    return await service.update(video_id, video_data)


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
        video_id: int,
        service: VideoService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    video = await service.get(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video doesn't exist"
        )
    if video.author.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have permission"
        )

    await service.delete(video_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{video_od}/likes", response_model=List[UserSchema])
async def get_video_likes(
        video_id: int,
        service: VideoService = Depends()
):
    video = await service.get(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video doesn't exist"
        )

    return await service.get_like_list(video_id)


@router.post("/{video_id}/likes", tags=["likes"], status_code=status.HTTP_201_CREATED)
async def like_video(
        video_id: int,
        service: VideoService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    video = await service.get(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video doesn't exist"
        )
    if user in await service.get_like_list(video_id):
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You already liked this video"
        )
    await service.like(video_id, user.id)
    return Response(status_code=status.HTTP_201_CREATED)


@router.delete("/{video_id}/likes", tags=["likes"], status_code=status.HTTP_204_NO_CONTENT)
async def unlike_video(
        video_id: int,
        service: VideoService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    video = await service.get(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video doesn't exist"
        )
    if user not in await service.get_like_list(video_id):
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You have not liked this video before"
        )

    await service.unlike(video_id, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
