import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File,Query
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil, os

from app.database.db import get_db
from app.models.note import Note
from app.models.tag import Tag
from app.models.user import User
from app.models.category import Category
from app.schemas.note import NoteCreate, NoteOut, NoteUpdate,CategoryOut,PaginatedNotes
from app.auth.dependencies import get_current_user


# --- Setup logger ---
logger = logging.getLogger("notes_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/errors.log")
file_handler.setLevel(logging.ERROR)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

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
    try:
        tags_input = note.tags or []

        if len(tags_input) == 1 and isinstance(tags_input[0], str) and "," in tags_input[0]:
            tags_input = [t.strip() for t in tags_input[0].split(",") if t.strip()]

        tags_input = list(set([t.strip().lower() for t in tags_input if t.strip()]))

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
            category = db.query(Category).filter(
                Category.id == note.category_id
            ).first()

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

    except HTTPException:
        logger.exception( 
            f"[POST /notes] Error creating note | user_id={current_user.id}"
        )
        raise

    except Exception:
        db.rollback()
        logger.exception(
            f"[POST /notes] Error creating note | user_id={current_user.id}"
        )
        raise

@router.get("/", response_model=PaginatedNotes)
def get_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1)
):
    try:
        query = db.query(Note).filter(Note.user_id == current_user.id)
        total_notes = query.count()
        offset = (page - 1) * limit

        notes = query.order_by(Note.id).offset(offset).limit(limit).all()
        total_pages = (total_notes + limit - 1) // limit

        logger.info(
            f"Fetched {len(notes)} notes for user_id={current_user.id} | "
            f"page={page} | limit={limit}"
        )

        return {
            "total": total_notes,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "data": [
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
        }

    except Exception as e:
        logger.exception(
            f"Error fetching notes for user_id={current_user.id} | page={page} | limit={limit}"
        )
        raise e


@router.get("/{id}", response_model=NoteOut)
def get_note(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        note = db.query(Note).filter(
            Note.id == id,
            Note.user_id == current_user.id
        ).first()

        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        return NoteOut(
            id=note.id,
            title=note.title,
            content=note.content,
            user_id=note.user_id,
            tags=[tag.name for tag in note.tags],
            category=note.category.name if note.category else None,
            file_path=note.file_path
        )

    except HTTPException:
        logger.exception(
            f"[GET /notes/{id}] Error | user_id={current_user.id}"
        )
        raise

    except Exception:
        logger.exception(
            f"[GET /notes/{id}] Error | user_id={current_user.id}"
        )
        raise


@router.put("/{id}", response_model=NoteOut)
def update_note(
    id: int,
    note_data: NoteUpdate = Depends(),
    db: Session = Depends(get_db),
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_user)
):
    try:
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

        tags_input = list(set([t.strip().lower() for t in tags_input if t.strip()]))

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
            category = db.query(Category).filter(
                Category.id == note_data.category
            ).first()

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

    except HTTPException:
        logger.exception(
            f"[PUT /notes/{id}] Error | user_id={current_user.id}"
        )
        raise

    except Exception:
        logger.exception(
            f"[PUT /notes/{id}] Error | user_id={current_user.id}"
        )
        raise



@router.delete("/{id}")
def delete_note(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        note = db.query(Note).filter(
            Note.id == id,
            Note.user_id == current_user.id
        ).first()

        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        db.delete(note)
        db.commit()

       

        return {"message": "Note deleted successfully"}

    except HTTPException:
        logger.exception(
            f"[DELETE /notes/{id}] Error | user_id={current_user.id}"
        )   
        raise

    except Exception:
        logger.exception(
            f"[DELETE /notes/{id}] Error | user_id={current_user.id}"
        )
        raise