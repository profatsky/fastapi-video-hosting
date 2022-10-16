import shutil
from datetime import datetime
from os import makedirs
from uuid import uuid4

from fastapi import Depends, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi.background import BackgroundTasks

from app.database.database import get_session
from app.models.videos import VideoModel
from app.schemas.videos import VideoCreateSchema, VideoSchema


class VideoService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def _get(self, video_id: int) -> VideoSchema | None:
        video = await self.session.execute(
            select(VideoModel)
            .options(joinedload(VideoModel.author))
            .where(VideoModel.id == video_id)
        )
        video = video.scalar()
        if not video:
            return
        return VideoSchema.from_orm(video)

    async def get(self, video_id: int) -> VideoSchema | None:
        return await self._get(video_id)

    async def create(
            self, background_tasks: BackgroundTasks, file: UploadFile, video_data: VideoCreateSchema
    ) -> VideoSchema | None:
        file_path = f"app/videos/{video_data.author.id}/{uuid4()}.mp4"

        background_tasks.add_task(
            self.save_video,
            file,
            file_path
        )

        video = VideoModel(
            title=video_data.title,
            description=video_data.description,
            author_id=video_data.author.id,
            file=file_path,
            created_at=datetime.now()
        )
        self.session.add(video)
        await self.session.commit()

        return VideoSchema(
            id=video.id,
            title=video.title,
            description=video.description,
            created_at=video.created_at,
            file=video.file,
            author=video_data.author
        )

    @staticmethod
    def save_video(file: UploadFile, file_path: str):
        makedirs(file_path.rsplit("/", 1)[0], exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
