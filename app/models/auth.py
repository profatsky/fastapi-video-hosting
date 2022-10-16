from sqlalchemy import Column, Integer, String

from app.database.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    username = Column(String(50))
    password = Column(String)
