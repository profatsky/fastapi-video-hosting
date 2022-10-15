from app.config import settings


def get_sqlalchemy_url() -> str:
    return "postgresql+asyncpg://{user}:{password}@{host}/{database}".format(
        user=settings.user, password=settings.password,
        host=settings.host, database=settings.database
    )
