# backend/app/main.py

from fastapi import FastAPI
from users import router as users_router
from agents import router as agents_router
from rag import router as rag_router
from dotenv import load_dotenv
from database import engine, Base

load_dotenv()

app = FastAPI()

app.include_router(users_router)
app.include_router(agents_router)
app.include_router(rag_router)

# you can test if the connection is made or not
try:
    with engine.connect() as connection_str:
        print('Successfully connected to the PostgreSQL database')
        # Base.metadata.create_all(bind=engine)
except Exception as ex:
    print(f'Sorry failed to connect: {ex}')