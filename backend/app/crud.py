# backend/app/crud.py

from sqlalchemy.orm import Session
import models, schemas
from security import get_password_hash
from dependencies import generate_random_id

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(id=generate_random_id(), email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_agent(db: Session, agent_id: int):
    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()

# def create_agent(db: Session, agent: schemas.AgentCreate, user_id: int):
#     db_agent = models.Agent(**agent.dict(), owner_id=user_id)
#     db.add(db_agent)
#     db.commit()
#     db.refresh(db_agent)
#     return db_agent