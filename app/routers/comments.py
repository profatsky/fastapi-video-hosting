from typing import List

from fastapi import Depends, APIRouter, status, Response

from app.dependencies.comments import valid_comment_id, valid_owned_comment
from app.dependencies.videos import valid_video_id
from app.models import VideoModel, CommentModel
from app.schemas.exceptions import MessageSchema
from app.schemas.users import UserSchema
from app.schemas.comments import CommentCreateSchema, CommentUpdateSchema, CommentSchema
from app.dependencies.auth import get_current_user
from app.services.comments import CommentService

router = APIRouter(
    prefix="/videos",
    tags=["comments"]
)


@router.post(
    "/{video_id}/comments",
    response_model=CommentSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": CommentSchema,
            "description": "New comment left"
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
async def leave_comment(
        comment: CommentCreateSchema,
        video: VideoModel = Depends(valid_video_id),
        comment_service: CommentService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    """
    Leave a comment on a video

    **video_id**: video id\n
    **comment**: comment id answered by user and text
    """
    return await comment_service.create(video.id, comment, user)


@router.get(
    "/{video_id}/comments",
    response_model=List[CommentSchema],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[CommentSchema],
            "description": "Received list of comments"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "Video doesn't exist"
        }
    }
)
async def get_list_comments(
        video: VideoModel = Depends(valid_video_id),
        service: CommentService = Depends()
):
    """
    Get a list of comments on a video

    **video_id**: video id
    """
    return await service.get_list(video.id)


@router.get(
    "/{video_id}/comments/{comment_id}",
    response_model=CommentSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(valid_video_id)],
    responses={
        status.HTTP_200_OK: {
            "model": CommentSchema,
            "description": "Comment received"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "Video or comment doesn't exist"
        }
    }
)
async def get_comment(
        comment: CommentModel = Depends(valid_comment_id)
):
    """
    Get a comment on a video

    **video_id**: video id\n
    **comment_id**: comment id
    """
    return comment


@router.patch(
    "/{video_id}/comments/{comment_id}",
    response_model=CommentSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(valid_video_id)],
    responses={
        status.HTTP_200_OK: {
            "model": CommentSchema,
            "description": "Comment updated"
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
            "description": "Video or comment doesn't exist"
        }
    }
)
async def update_comment(
        comment_data: CommentUpdateSchema,
        comment: CommentModel = Depends(valid_owned_comment),
        service: CommentService = Depends()
):
    """
    Update a comment on a video

    **video_id**: video id\n
    **comment_id**: comment id\n
    **comment_data**: new comment text
    """
    return await service.update(comment.id, comment_data)


@router.delete(
    "/{video_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(valid_video_id)],
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
            "description": "Video or comment doesn't exist"
        }
    }
)
async def delete_comment(
        comment: CommentModel = Depends(valid_owned_comment),
        service: CommentService = Depends()
):
    """
    Delete a comment on a video

    **video_id**: video id\n
    **comment_id**: comment id
    """
    await service.delete(comment.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
