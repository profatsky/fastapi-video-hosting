from datetime import datetime

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.models.comments import CommentModel
from app.schemas.auth import UserSchema
from app.schemas.comments import CommentCreateSchema


class CommentService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def _get(self, comment_id: int) -> CommentModel | None:
        comment = await self.session.execute(
            select(CommentModel)
            .where(CommentModel.id == comment_id)
        )
        comment = comment.scalar()
        if not comment:
            return
        return comment

    async def get(self, comment_id: int) -> CommentModel | None:
        return await self._get(comment_id)

    async def create(self, video_id: int, comment: CommentCreateSchema, user: UserSchema) -> CommentModel:
        comment = CommentModel(
            **comment.dict(),
            author_id=user.id,
            video_id=video_id,
            created_at=datetime.now()
        )
        self.session.add(comment)
        await self.session.commit()

        return comment
