# backend/app/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session
import users_manager, models, schemas
from dependencies import get_db
from database import settings
from security import get_password_hash, verify_password

sercurity = HTTPBearer()

def authenticate_user(db: Session, email: str, password: str):
    user = users_manager.get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def register_user(db: Session, user: schemas.UserCreate):
    return users_manager.create_user(db, user)

def get_current_user(db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(sercurity)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = users_manager.get_user_by_email(db, email=user_id)
    if user is None:
        raise credentials_exception
    return user