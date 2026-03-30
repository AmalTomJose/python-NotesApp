from pydantic import BaseModel
from typing import List, Optional

class NoteBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    category_id: Optional[int] = None  


class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = []
    category: Optional[str] = None
   


class CategoryOut(BaseModel):
    name: str

    class Config:
        orm_mode = True

class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    tags: List[str] = []
    category: Optional[str] = None

    file_path: Optional[str] =  None

    class Config:
        orm_mode = True

   