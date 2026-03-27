from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.association import note_tags

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    notes = relationship(
        "Note",
        secondary=note_tags,
        back_populates="tags"
    )