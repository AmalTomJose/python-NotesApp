
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.association import note_tags
from sqlalchemy.sql import func


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    file_path = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    
    user = relationship("User", back_populates="notes")
    tags = relationship(
        "Tag",
        secondary=note_tags,
        back_populates="notes"
    )
    category = relationship("Category", back_populates="notes")