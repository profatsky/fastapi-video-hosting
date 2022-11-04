from typing import List

from fastapi import Depends
from sqlalchemy import select, insert, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database.database import get_session
from app.models import UserModel, VideoModel, subscribers_table
from app.schemas.users import UserUpdateSchema, UserSchema
from app.services.base import BaseService


class UserService(BaseService):
    async def _get(self, user_id: int) -> UserModel | None:
        user = await self.session.execute(
            select(UserModel)
            .options(joinedload(UserModel.videos))
            .options(joinedload(UserModel.subscribers))
            .options(joinedload(UserModel.subscribe_to))
            .options(joinedload(UserModel.comments))
            .where(UserModel.id == user_id)
        )
        user = user.scalar()
        if not user:
            return
        return user

    async def get(self, user_id: int) -> UserModel | None:
        user = await self._get(user_id)
        if not user:
            return
        return user

    async def get_videos(self, user_id: int) -> List[VideoModel]:
        videos = await self.session.execute(
            select(VideoModel)
            .where(VideoModel.author_id == user_id)
        )
        videos = videos.scalars().all()
        return videos

    async def get_subscribers(self, user_id: int) -> List[int]:
        user = await self.session.execute(
            select(UserModel)
            .options(joinedload(UserModel.subscribers))
            .where(UserModel.id == user_id)
        )
        user = user.scalar()
        return [subscriber.id for subscriber in user.subscribers]

    async def update(self, user_id: int, user_data: UserUpdateSchema) -> UserModel:
        user = await self._get(user_id)
        for field, value in user_data:
            if value is not None:
                setattr(user, field, value)
        await self.session.commit()
        return user

    async def subscribe(self, author_id: int, user: UserSchema):
        if user.id not in await self.get_subscribers(author_id):
            await self.session.execute(
                insert(subscribers_table)
                .values(author_id=author_id, subscriber_id=user.id)
            )
            await self.session.commit()

    async def unsubscribe(self, author_id: int, user: UserSchema):
        if user.id in await self.get_subscribers(author_id):
            await self.session.execute(
                delete(subscribers_table)
                .where(and_(
                    subscribers_table.c.subscriber_id == user.id,
                    subscribers_table.c.author_id == author_id)
                )
            )
            await self.session.commit()
