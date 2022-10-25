from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.models import UserModel, VideoModel
from app.schemas.users import UserUpdateSchema


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def _get(self, user_id: int) -> UserModel | None:
        user = await self.session.execute(
            select(UserModel)
            .where(UserModel.id == user_id)
        )
        user = user.scalar()
        if not user:
            return
        return user

    async def get(self, user_id: int) -> UserModel | None:
        return await self._get(user_id)

    async def get_videos(self, user_id: int) -> List[VideoModel]:
        videos = await self.session.execute(
            select(VideoModel)
            .where(VideoModel.author_id == user_id)
        )
        videos = videos.scalars().all()
        return videos

    async def update(self, user_id: int, user_data: UserUpdateSchema) -> UserModel:
        user = await self._get(user_id)
        for field, value in user_data:
            if value is not None:
                setattr(user, field, value)
        await self.session.commit()
        return user

    async def delete(self, user_id):
        video = await self._get(user_id)
        await self.session.delete(video)
        await self.session.commit()
