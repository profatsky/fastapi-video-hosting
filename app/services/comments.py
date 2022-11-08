from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.comments import CommentModel
from app.schemas.users import UserSchema
from app.schemas.comments import CommentCreateSchema, CommentUpdateSchema, CommentSchema
from app.services.base import BaseService


class CommentService(BaseService):
    async def _get(self, comment_id: int) -> CommentModel | None:
        comment = await self.session.execute(
            select(CommentModel)
            .options(joinedload(CommentModel.author))
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
            .options(joinedload(CommentModel.author))
            .where(CommentModel.video_id == video_id)
        )
        comments = comments.scalars().all()
        return comments

    async def create(self, video_id: int, comment: CommentCreateSchema, user: UserSchema) -> CommentSchema:
        comment = CommentModel(
            **comment.dict(),
            author_id=user.id,
            video_id=video_id,
            created_at=datetime.now()
        )
        self.session.add(comment)
        await self.session.commit()

        return CommentSchema(
            id=comment.id,
            author=user,
            text=comment.text,
            created_at=comment.created_at,
            answer_to=comment.answer_to
        )

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
