# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.environ['DATABASE_URL']
    SECRET_KEY: str = os.environ['SECRET_KEY']
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
