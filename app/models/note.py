
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.association import note_tags

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(String)
    file_path = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    # relationships
    user = relationship("User", back_populates="notes")

    tags = relationship(
        "Tag",
        secondary=note_tags,
        back_populates="notes"
    )