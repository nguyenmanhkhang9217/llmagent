# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from llm import LLMType
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_HOST: str = os.environ['POSTGRES_HOST']
    POSTGRES_USER: str = os.environ['POSTGRES_USER']
    POSTGRES_PASSWORD: str = os.environ['POSTGRES_PASSWORD']
    POSTGRES_DB: str = os.environ['POSTGRES_DB']
    DATABASE_URL: str = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
    SECRET_KEY: str = os.environ['SECRET_KEY']
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

llm_types = [ 
    LLMType.CHROMA, 
    LLMType.PINECONE 
]

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
