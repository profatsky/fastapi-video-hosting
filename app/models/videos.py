from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Table
from sqlalchemy.orm import relationship

from app.database.database import Base


class VideoModel(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    description = Column(String(500))
    file = Column(String(1000))
    created_at = Column(TIMESTAMP)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    comments = relationship("CommentModel", cascade="all,delete")
    author = relationship("UserModel", back_populates="videos")
    likes = relationship(
        "UserModel",
        secondary="videos_likes"
    )


likes_table = Table(
    "videos_likes",
    Base.metadata,
    Column("video_id", Integer, ForeignKey("videos.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
)
