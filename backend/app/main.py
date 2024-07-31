from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
# import pinecone
from routes import agents, conversations, files, users
from database import engine
from models import Base
# import os

app = FastAPI()

# Create all tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(files.router, prefix="/api")