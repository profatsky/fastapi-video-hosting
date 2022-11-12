import os

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.app import app
from app.database.database import Base, get_session
from app.database.db_config import get_sqlalchemy_url
from app.schemas.users import UserCreateSchema

engine = create_async_engine(
    get_sqlalchemy_url(database="test"),
    echo=True,
    future=True
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


@pytest.fixture(scope="session")
async def session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        yield session


@pytest.fixture(scope="session")
async def client(session):
    async def _override_get_db():
        try:
            yield session
        finally:
            await session.close()

    app.dependency_overrides[get_session] = _override_get_db
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as cli:
        yield cli


@pytest.fixture
async def user_to_create():
    yield UserCreateSchema(
        username="test",
        email="test@test.com",
        password="qwerty"
    )


@pytest.fixture
async def authorized_client_token(client, user_to_create):
    await client.post(
        "/auth/sign-up",
        json=user_to_create.dict()
        )
    resp = await client.post(
        "/auth/sign-in",
        data={
            "username": "test@test.com",
            "password": "qwerty"
        }
    )
    yield resp.json()["access_token"]


@pytest.fixture
async def video_file():
    yield {
        'file': (
            "video_test.mp4",
            open(os.path.join(os.path.dirname(__file__), "assets/video_test.mp4"), "rb"),
            "video/mp4"
        )
    }


@pytest.fixture
async def uploaded_video_id(client, authorized_client_token, video_file):
    resp = await client.post(
        "/videos/upload",
        data={
            "title": "test video",
            "description": "test description"
        },
        files=video_file,
        headers={"Authorization": f"Bearer {authorized_client_token}"}
    )
    video_id = resp.json()["id"]
    yield video_id
    await client.delete(
        f"/videos/{video_id}",
        headers={"Authorization": f"Bearer {authorized_client_token}"}
    )


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
