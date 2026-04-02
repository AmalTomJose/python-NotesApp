from sqlalchemy import Column, Integer, ForeignKey
from app.database.base import Base

class Favourite(Base):
    __tablename__ = "favourites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    note_id = Column(Integer, ForeignKey("notes.id"))

