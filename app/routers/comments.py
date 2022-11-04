from typing import List

from fastapi import Depends, APIRouter, status, Response

from app.dependencies.comments import valid_comment_id, valid_owned_comment
from app.dependencies.videos import valid_video_id
from app.models import VideoModel, CommentModel
from app.schemas.users import UserSchema
from app.schemas.comments import CommentCreateSchema, CommentUpdateSchema, CommentSchema
from app.dependencies.auth import get_current_user
from app.services.comments import CommentService

router = APIRouter(
    prefix="/videos",
    tags=["comments"]
)


@router.post("/{video_id}/comments", response_model=CommentSchema, status_code=status.HTTP_201_CREATED)
async def leave_comment(
        comment: CommentCreateSchema,
        video: VideoModel = Depends(valid_video_id),
        comment_service: CommentService = Depends(),
        user: UserSchema = Depends(get_current_user)
):

    return await comment_service.create(video.id, comment, user)


@router.get("/{video_id}/comments", response_model=List[CommentSchema])
async def get_list_comments(
        video: VideoModel = Depends(valid_video_id),
        service: CommentService = Depends()
):
    return await service.get_list(video.id)


@router.get("/{video_id}/comments/{comment_id}", response_model=CommentSchema)
async def get_comment(
        video: VideoModel = Depends(valid_video_id),
        comment: CommentModel = Depends(valid_comment_id)
):
    return comment


@router.patch("/{video_id}/comments/{comment_id}", response_model=CommentSchema)
async def update_comment(
        comment_data: CommentUpdateSchema,
        video: VideoModel = Depends(valid_video_id),
        comment: CommentModel = Depends(valid_owned_comment),
        service: CommentService = Depends()
):
    return await service.update(comment.id, comment_data)


@router.delete("/{video_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        video: VideoModel = Depends(valid_video_id),
        comment: CommentModel = Depends(valid_owned_comment),
        service: CommentService = Depends()
):
    await service.delete(comment.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
