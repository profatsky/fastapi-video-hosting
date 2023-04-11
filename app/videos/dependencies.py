from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.users.schemas import UserSchema
from .models import VideoModel
from .services import VideoService


async def valid_video_id(
        video_id: int,
        service: VideoService = Depends()
) -> VideoModel:
    video = await service.get(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video doesn't exist"
        )
    return video


async def valid_owned_video(
        video: VideoModel = Depends(valid_video_id),
        user: UserSchema = Depends(get_current_user)
) -> VideoModel:
    if video.author.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have permission"
        )
    return video
