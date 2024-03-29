from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.comments.models import CommentModel
from app.users.schemas import UserSchema
from app.comments.services import CommentService


async def valid_comment_id(
        comment_id: int,
        service: CommentService = Depends()
) -> CommentModel:
    comment = await service.get(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment doesn't exist"
        )
    return comment


async def valid_owned_comment(
        comment: CommentModel = Depends(valid_comment_id),
        user: UserSchema = Depends(get_current_user)
) -> CommentModel:
    if comment.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have permission"
        )
    return comment

