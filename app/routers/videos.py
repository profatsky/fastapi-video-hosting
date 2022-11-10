from typing import List

from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException, status, BackgroundTasks, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.dependencies.videos import valid_video_id, valid_owned_video
from app.models import VideoModel
from app.schemas.exceptions import MessageSchema
from app.schemas.users import UserSchema
from app.schemas.videos import VideoCreateSchema, VideoSchema, VideoUpdateSchema
from app.dependencies.auth import get_current_user
from app.services.videos import VideoService


templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/videos",
    tags=["videos"]
)


@router.post(
    "/upload",
    response_model=VideoSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": VideoSchema,
            "description": "Video successfully uploaded"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": MessageSchema,
            "description": "Could not validate credentials"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "Video doesn't exist"
        },
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {
            "model": MessageSchema,
            "description": "File type must be mp4"
        }
    }
)
async def upload_video(
        background_tasks: BackgroundTasks,
        title: str = Form(...),
        description: str = Form(...),
        file: UploadFile = File(...),
        service: VideoService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    """
    Upload a video

    **title**: video title\n
    **description**: video description\n
    **file**: MP4 file
    """
    if file.content_type != "video/mp4":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File type must be mp4"
        )
    video_data = VideoCreateSchema(title=title, description=description, author=user)
    return await service.create(background_tasks, file, video_data)


@router.get(
    "/{video_id}",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Received HTML template"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "Video doesn't exist"
        }
    }
)
async def get_video(
        request: Request,
        video: VideoModel = Depends(valid_video_id)
):
    """
    Get HTML template with player for watching video

    **video_id**: video id
    """
    return templates.TemplateResponse(
        "videos.html", {"request": request, "video_data": video}
    )


@router.get(
    "/{video_id}/watching",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Watching video"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "Video doesn't exist"
        }
    }
)
async def get_streaming_video(
        request: Request,
        service: VideoService = Depends(),
        video: VideoModel = Depends(valid_video_id)
) -> StreamingResponse:
    """
    Get streaming video for watching

    **video_id**: video id
    """
    file, status_code, content_length, headers = await service.open_file(request, video.id)
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


@router.patch(
    "/{video_id}",
    response_model=VideoSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": VideoSchema,
            "description": "Video's info updated"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": MessageSchema,
            "description": "Could not validate credentials"
        },
        status.HTTP_403_FORBIDDEN: {
            "model": MessageSchema,
            "description": "Don't have permission"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "Video doesn't exist"
        }
    }
)
async def update_video(
        video_data: VideoUpdateSchema,
        video: VideoModel = Depends(valid_owned_video),
        service: VideoService = Depends(),
):
    """
    Update video info

    **video_id**: video id\n
    **video_data**: video title and description
    """
    return await service.update(video.id, video_data)


@router.delete(
    "/{video_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": MessageSchema,
            "description": "Could not validate credentials"
        },
        status.HTTP_403_FORBIDDEN: {
            "model": MessageSchema,
            "description": "Don't have permission"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "Video doesn't exist"
        }
    }
)
async def delete_video(
        video: VideoModel = Depends(valid_owned_video),
        service: VideoService = Depends()
):
    """
    Delete a video

    **video_id**: video id
    """
    await service.delete(video.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{video_id}/likes",
    response_model=List[UserSchema],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[UserSchema],
            "description": "Received list of users"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "Video doesn't exist"
        }
    }
)
async def get_video_likes(
        video: VideoModel = Depends(valid_video_id)
):
    """
    Get a list of users who liked the video

    **video_id**: video id
    """
    return video.likes


@router.put(
    "/{video_id}/likes",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": MessageSchema,
            "description": "Video liked"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": MessageSchema,
            "description": "Could not validate credentials"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "Video doesn't exist"
        }
    }
)
async def like_video(
        user: UserSchema = Depends(get_current_user),
        video: VideoModel = Depends(valid_video_id),
        service: VideoService = Depends()
):
    """
    Like a video

    **video_id**: video id
    """
    if user.id in await service.get_like_list(video.id):
        await service.like(video.id, user.id)
    return Response(status_code=status.HTTP_200_OK)


@router.delete(
    "/{video_id}/likes",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": MessageSchema,
            "description": "Video liked"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": MessageSchema,
            "description": "Could not validate credentials"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "Video doesn't exist"
        }
    }
)
async def unlike_video(
        user: UserSchema = Depends(get_current_user),
        video: VideoModel = Depends(valid_video_id),
        service: VideoService = Depends()
):
    """
    Unlike a video

    **video_id**: video id
    """
    if user.id not in await service.get_like_list(video.id):
        await service.unlike(video.id, user.id)
    return Response(status_code=status.HTTP_200_OK)
