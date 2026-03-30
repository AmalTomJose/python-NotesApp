from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil, os

from app.database.db import get_db
from app.models.note import Note
from app.models.tag import Tag
from app.models.user import User
from app.models.category import Category
from app.schemas.note import NoteCreate, NoteOut, NoteUpdate,CategoryOut
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/notes", tags=["Notes"])

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/categories", response_model=List[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories           



@router.post("/", response_model=NoteOut)
def create_note(
    note: NoteCreate = Depends(),
    db: Session = Depends(get_db),
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_user)
):

    tags_input = note.tags or []

    if len(tags_input) == 1 and isinstance(tags_input[0], str) and "," in tags_input[0]:
        tags_input = [t.strip() for t in tags_input[0].split(",") if t.strip()]

    db_tags = []
    for tag_name in tags_input:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        db_tags.append(tag)

   
    file_path = None
    if file:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    category = None
    if note.category_id:
        category = db.query(Category).filter(Category.id == note.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")


    db_note = Note(
        title=note.title,
        content=note.content,
        user_id=current_user.id,
        tags=db_tags,
        category_id=note.category_id,
        file_path=file_path
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)


    return NoteOut(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        user_id=db_note.user_id,
        tags=[tag.name for tag in db_note.tags],
        category=category.name if category else None,
        file_path=db_note.file_path
    )


@router.get("/", response_model=List[NoteOut])
def get_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notes = db.query(Note).filter(Note.user_id == current_user.id).all()

    return [
        NoteOut(
            id=n.id,
            title=n.title,
            content=n.content,
            user_id=n.user_id,
            tags=[tag.name for tag in n.tags],
            category=n.category.name if n.category else None,
            file_path=n.file_path
        )
        for n in notes
    ]



@router.get("/{id}", response_model=NoteOut)
def get_note(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(
        Note.id == id,
        Note.user_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return  NoteOut(
        id=note.id,
        title=note.title,
        content=note.content,  
        user_id=note.user_id,
        tags=[tag.name for tag in note.tags],
        category=note.category.name if note.category else None,

        file_path=note.file_path
    )


@router.put("/{id}", response_model=NoteOut)
def update_note(
    id: int,
    note_data: NoteUpdate = Depends(),   
    db: Session = Depends(get_db),
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(
        Note.id == id,
        Note.user_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note_data.title is not None:
        note.title = note_data.title

    if note_data.content is not None:
        note.content = note_data.content

    tags_input = note_data.tags or []

    if len(tags_input) == 1 and isinstance(tags_input[0], str) and "," in tags_input[0]:
        tags_input = [t.strip() for t in tags_input[0].split(",") if t.strip()]

    db_tags = []
    for tag_name in tags_input:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        db_tags.append(tag)

    if tags_input:
        note.tags = db_tags

    if note_data.category is not None:
        category = db.query(Category).filter(Category.id == note_data.category).first()
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category_id")
        note.category_id = note_data.category

    if file:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        note.file_path = file_path
       
    db.commit()
    db.refresh(note)

    return NoteOut(
        id=note.id,
        title=note.title,
        content=note.content,
        user_id=note.user_id,
        tags=[tag.name for tag in note.tags],
        category=note.category.name if note.category else None,
        file_path=note.file_path
    )

@router.delete("/{id}")
def delete_note(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(
        Note.id == id,
        Note.user_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()

    return {"message": "Note deleted successfully"}