
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.user import User
from app.models.note import Note
from app.models.shared_note import SharedNote
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/share", tags=["Share"])


@router.post("/")
def share_note(
    note_id: int,
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found or not yours")

    target_user = db.query(User).filter(User.email == username).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot share with yourself")

    existing = db.query(SharedNote).filter(
        SharedNote.note_id == note_id,
        SharedNote.shared_with_id == target_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already shared")

    shared_note = SharedNote(
        note_id=note_id,
        owner_id=current_user.id,
        shared_with_id=target_user.id
    )

    db.add(shared_note)
    db.commit()

    return {"message": "Note shared successfully"}




@router.get("/getsharednote")
def get_notes_shared_to_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    shared_notes = db.query(SharedNote).filter(
        SharedNote.shared_with_id == current_user.id
    ).all()

    result = []

    for shared in shared_notes:
        note = db.query(Note).filter(Note.id == shared.note_id).first()
        owner = db.query(User).filter(User.id == shared.owner_id).first()

        result.append({
            "note_id": note.id,
            "title": note.title,
            "content": note.content,
            "shared_by": owner.email
        })

    return result


@router.get("/sharednotes")
def get_notes_i_shared(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    shared_notes = db.query(SharedNote).filter(
        SharedNote.owner_id == current_user.id
    ).all()

    result = []

    for shared in shared_notes:
        note = db.query(Note).filter(Note.id == shared.note_id).first()
        user = db.query(User).filter(User.id == shared.shared_with_id).first()

        result.append({
            "note_id": note.id,
            "title": note.title,
            "content": note.content,
            "shared_to": user.email
        })

    return result