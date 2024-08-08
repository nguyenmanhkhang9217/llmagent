from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from routes import include_routers
from config import engine
from models import Base
# import os

app = FastAPI()

# Create all tables
Base.metadata.create_all(bind=engine)

# Include routers
app = include_routers(app)