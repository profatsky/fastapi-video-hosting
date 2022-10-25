from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship

from app.database.database import Base


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    text = Column(String(50))
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), index=True)
    created_at = Column(TIMESTAMP)
    answer_to = Column(Integer, ForeignKey("comments.id", ondelete="SET NULL"), index=True, nullable=True)
    author = relationship("UserModel", back_populates="comments")
