from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.database.db_config import get_sqlalchemy_url

engine = create_async_engine(
    get_sqlalchemy_url(),
    echo=True,
    future=True
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
