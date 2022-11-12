from app.config import settings


def get_sqlalchemy_url(
        user=settings.user,
        password=settings.password,
        host=settings.host,
        database=settings.database
) -> str:
    return "postgresql+asyncpg://{user}:{password}@{host}/{database}".format(
        user=user,
        password=password,
        host=host,
        database=database
    )
