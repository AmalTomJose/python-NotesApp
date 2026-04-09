
from sqlalchemy import Column, Integer, ForeignKey
from app.database.base import Base

class SharedNote(Base):
    __tablename__ = "shared_notes"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    shared_with_id = Column(Integer, ForeignKey("users.id"))