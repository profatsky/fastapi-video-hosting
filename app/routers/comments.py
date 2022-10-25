from typing import List

from fastapi import Depends, APIRouter, HTTPException, status, Response

from app.schemas.users import UserSchema
from app.schemas.comments import CommentCreateSchema, CommentUpdateSchema, CommentSchema
from app.services.auth import get_current_user
from app.services.comments import CommentService
from app.services.videos import VideoService

router = APIRouter(
    prefix="/videos",
    tags=["comments"]
)


@router.post("/{video_id}/comments", response_model=CommentSchema)
async def leave_comment(
        video_id: int,
        comment: CommentCreateSchema,
        video_service: VideoService = Depends(),
        comment_service: CommentService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    video = await video_service.get(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video doesn't exist"
        )

    return await comment_service.create(video_id, comment, user)


@router.get("/{video_id}/comments", response_model=List[CommentSchema])
async def get_list_comments(
        video_id: int,
        video_service: VideoService = Depends(),
        service: CommentService = Depends()
):
    video = await video_service.get(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video doesn't exist"
        )

    return await service.get_list(video_id)


@router.get("/{video_id}/comments/{comment_id}", response_model=CommentSchema)
async def get_comment(
        video_id: int,
        comment_id: int,
        video_service: VideoService = Depends(),
        comment_service: CommentService = Depends()
):
    video = await video_service.get(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video doesn't exist"
        )

    comment = await comment_service.get(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment doesn't exist"
        )

    return comment


@router.put("/{video_id}/comments/{comment_id}", response_model=CommentSchema)
async def update_comment(
        video_id: int,
        comment_id: int,
        comment_data: CommentUpdateSchema,
        video_service: VideoService = Depends(),
        comment_service: CommentService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    video = await video_service.get(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video doesn't exist"
        )

    comment = await comment_service.get(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment doesn't exist"
        )
    if comment.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have permission"
        )

    return await comment_service.update(comment_id, comment_data)


@router.delete("/{video_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        video_id: int,
        comment_id: int,
        video_service: VideoService = Depends(),
        comment_service: CommentService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    video = await video_service.get(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video doesn't exist"
        )

    comment = await comment_service.get(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment doesn't exist"
        )
    if comment.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have permission"
        )

    await comment_service.delete(comment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
