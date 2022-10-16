from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
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
    comments = relationship("CommentModel")
    author = relationship("UserModel")


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    text = Column(String(50))
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), index=True)
    answer_to = Column(Integer, ForeignKey("comments.id", ondelete="SET NULL"), index=True)
