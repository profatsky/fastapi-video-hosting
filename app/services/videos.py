import shutil
from datetime import datetime
from os import makedirs
from pathlib import Path
from uuid import uuid4
from typing import IO, Generator

from fastapi import Depends, UploadFile
from sqlalchemy import select, delete, and_, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi.background import BackgroundTasks
from fastapi.requests import Request

from app.database.database import get_session
from app.models.videos import VideoModel, likes_table
from app.schemas.videos import VideoCreateSchema, VideoSchema, VideoUpdateSchema


class VideoService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def _get(self, video_id: int) -> VideoModel | None:
        video = await self.session.execute(
            select(VideoModel)
            .options(joinedload(VideoModel.author))
            .options(joinedload(VideoModel.comments))
            .where(VideoModel.id == video_id)
        )
        video = video.scalar()
        if not video:
            return
        return video

    async def get(self, video_id: int) -> VideoModel | None:
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

    async def open_file(self, request: Request, video_id: int) -> tuple | None:
        video = await self._get(video_id)
        path = Path(video.file)
        file = path.open("rb")
        content_length = file_size = path.stat().st_size

        status_code = 200
        headers = {}
        content_range = request.headers.get("range")

        if content_range is not None:
            content_range = content_range.strip().lower()
            content_ranges = content_range.split('=')[-1]
            range_start, range_end, *_ = map(str.strip, (content_ranges + '-').split('-'))
            range_start = max(0, int(range_start)) if range_start else 0
            range_end = min(file_size - 1, int(range_end)) if range_end else file_size - 1
            content_length = (range_end - range_start) + 1
            file = self.ranged(file, start=range_start, end=range_end + 1)
            status_code = 206
            headers['Content-Range'] = f'bytes {range_start}-{range_end}/{file_size}'

        return file, status_code, content_length, headers

    @staticmethod
    def ranged(
            file: IO[bytes],
            start: int = 0,
            end: int = None,
            block_size: int = 8192,
    ) -> Generator[bytes, None, None]:
        consumed = 0
        file.seek(start)
        while True:
            data_length = min(block_size, end - start - consumed) if end else block_size
            if data_length <= 0:
                break
            data = file.read(data_length)
            if not data:
                break
            consumed += data_length
            yield data

        if hasattr(file, 'close'):
            file.close()

    async def update(self, video_id: int, video_data: VideoUpdateSchema):
        video = await self._get(video_id)
        for field, value in video_data:
            if value is not None:
                setattr(video, field, value)
        await self.session.commit()
        return video

    async def delete(self, video_id: int):
        video = await self._get(video_id)
        await self.session.delete(video)
        await self.session.commit()

    async def like(self, video_id: int, user_id: int):
        try:
            await self.session.execute(
                insert(likes_table)
                .values(video_id=video_id, user_id=user_id)
            )
            await self.session.commit()
        except IntegrityError:
            return

    async def unlike(self, video_id: int, user_id: int):
        await self.session.execute(
            delete(likes_table)
            .where(and_(
                likes_table.c.video_id == video_id,
                likes_table.c.user_id == user_id)
            )
        )
        await self.session.commit()
