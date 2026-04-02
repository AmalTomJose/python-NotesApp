from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.database.db import get_db
from app.models.favourite import Favourite
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.note import Note

logger = logging.getLogger("favourites_logger")
router = APIRouter(prefix="/favourites", tags=["Favourites"])


@router.post("/{note_id}")
def add_favourite(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        note = db.query(Note).filter(
            Note.id == note_id,
            Note.user_id == current_user.id
        ).first()

        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        existing_fav = db.query(Favourite).filter_by(
            user_id=current_user.id,
            note_id=note_id
        ).first()

        if existing_fav:
            raise HTTPException(status_code=400, detail="Already in favourites")

        fav = Favourite(user_id=current_user.id, note_id=note_id)

        db.add(fav)
        db.commit()
        db.refresh(fav)

        return {
            "message": "Note added to favourites",
            "favourite_id": fav.id
        }

    except HTTPException:
        logger.exception(
            f"[POST /favourites] Failed | user_id={current_user.id}"
        )
        raise
    except Exception:
        logger.exception(
            f"[POST /favourites] Server error | user_id={current_user.id}"
        )
        raise


@router.delete("/{note_id}")
def remove_favourite(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        fav = db.query(Favourite).filter_by(
            user_id=current_user.id,
            note_id=note_id
        ).first()

        if not fav:
            raise HTTPException(status_code=404, detail="Favourite not found")

        db.delete(fav)
        db.commit()

        return {"message": "Removed from favourites"}

    except Exception:
        logger.exception(
            f"[DELETE /favourites/{note_id}] Error | user_id={current_user.id}"
        )
        raise


@router.get("/")
def get_favourites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        favs = db.query(Favourite).filter_by(
            user_id=current_user.id
        ).all()

        # ✅ Return notes cleanly
        return [
            {
                "id": fav.note.id,
                "title": fav.note.title,
                "content": fav.note.content,
                "category": fav.note.category.name if fav.note.category else None
            }
            for fav in favs
        ]

    except Exception:
        logger.exception(
            f"[GET /favourites] Error | user_id={current_user.id}"
        )
        raise