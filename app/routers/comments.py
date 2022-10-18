from fastapi import Depends

from app.routers.videos import router
from app.schemas.auth import UserSchema
from app.schemas.comments import CommentCreateSchema
from app.services.auth import get_current_user
from app.services.comments import CommentService


@router.post("/{video_id}")
async def leave_comment(
        video_id: int,
        comment: CommentCreateSchema,
        service: CommentService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    return await service.create(video_id, comment, user)
