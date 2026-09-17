"""User registration and login endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import AuthRequest, TokenResponse
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: AuthRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    """Create a user and return an access token."""
    email = request.email.lower()
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="email already registered")

    user = User(email=email, password_hash=hash_password(request.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id), email=user.email)


@router.post("/login", response_model=TokenResponse)
def login(request: AuthRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    """Authenticate a user and return an access token."""
    email = request.email.lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id), email=user.email)
