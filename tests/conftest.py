import os

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.app import app
from app.database.database import Base, get_session
from app.database.db_config import get_sqlalchemy_url

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


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
