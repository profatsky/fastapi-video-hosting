from pydantic import BaseSettings


class Settings(BaseSettings):
    host: str
    port: int
    user: str
    password: str
    database: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 36000


settings = Settings(
    _env_file=".env",
    _env_file_encoding="utf-8",
)
