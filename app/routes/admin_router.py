from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.note import Note


router = APIRouter(prefix = '/admin', tags = ['Admin'])

@router.get('/users')
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.isAdmin:
        raise HTTPException(status_code=403, detail="Access denied,only admin allowed")
    total_users = db.query(User).filter(User.isAdmin == False).all()

    return {
        "total_users": len(total_users),
        "users": [
            {
                "id": user.id,
                "email": user.email
            }
            for user in total_users
        ]
    } 

@router.get('/dashboard')
def get_dashboard(
    db:Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.isAdmin:
        raise HTTPException(status_code=403, detail="Access denied,only admin allowed")
    
    total_notes = db.query(Note).all()

    return {
        "total_notes_count": len(total_notes),
        "total_notes": [
            {
                "id": note.id,
                "title": note.title,
                "user_id": note.user_id
            }
            for note in total_notes
        ]


    }

