from app.auth.logger_auth import logger
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token
from app.auth.utils import hash_password, verify_password
from app.auth.jwt import create_access_token



router = APIRouter(prefix="/auth", tags=["auth"])
# Signup
@router.post("/signup", response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = User(email=user.email, password=hash_password(user.password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    except HTTPException:
        logger.exception(f"[POST /auth/signup] HTTP error for email={user.email}")
        raise

    except Exception:
        db.rollback()
        logger.exception(f"[POST /auth/signup] Unexpected error for email={user.email}")
        raise


# Login
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token({"user_id": user.id})
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        logger.exception(f"[POST /auth/login] HTTP error for email={form_data.username}")
        raise

    except Exception:
        db.rollback()
        logger.exception(f"[POST /auth/login] Unexpected error for email={form_data.username}")
        raise