# backend/app/dependencies.py

from database import SessionLocal
import secrets
import string

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_random_id(length=12):
    characters = string.ascii_letters + string.digits  # Combination of letters and digits
    random_id = ''.join(secrets.choice(characters) for _ in range(length))
    return random_id