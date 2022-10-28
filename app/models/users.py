from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base

subscribers_table = Table(
    "subscribers",
    Base.metadata,
    Column("author_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("subscriber_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    username = Column(String(50))
    password = Column(String)
    subscribers = relationship(
        "UserModel",
        secondary="subscribers",
        primaryjoin=id == subscribers_table.c.author_id,
        secondaryjoin=id == subscribers_table.c.subscriber_id,
        back_populates="subscribe_to"
    )
    subscribe_to = relationship(
        "UserModel",
        secondary="subscribers",
        primaryjoin=id == subscribers_table.c.subscriber_id,
        secondaryjoin=id == subscribers_table.c.author_id,
        back_populates="subscribers"
    )
    videos = relationship("VideoModel", back_populates="author")
    comments = relationship("CommentModel", back_populates="author")
