from datetime import datetime
from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.models.comments import CommentModel
from app.schemas.auth import UserSchema
from app.schemas.comments import CommentCreateSchema, CommentUpdateSchema


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

    async def get_list(self, video_id: int) -> List[CommentModel]:
        comments = await self.session.execute(
            select(CommentModel)
            .where(CommentModel.video_id == video_id)
        )
        comments = comments.scalars().all()
        return comments

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

    async def update(self, comment_id: int, comment_data: CommentUpdateSchema):
        comment = await self._get(comment_id)
        for field, value in comment_data:
            if value is not None:
                setattr(comment, field, value)
        await self.session.commit()
        return comment

    async def delete(self, comment_id: int):
        comment = await self._get(comment_id)
        await self.session.delete(comment)
        await self.session.commit()
