# backend/app/routers/agents.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, crud, auth, models
from dependencies import get_db, generate_random_id
import google.generativeai as genai
import os

router = APIRouter()

@router.post("/agents/", response_model=schemas.Agent)
# def create_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
#     return crud.create_agent(db=db, agent=agent, user_id=current_user.id)
async def create_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    # new_agent = schemas.Agent(id=generate_random_id(), name=agent.name, user_id=current_user.id)
    db_agent = models.Agent(id=generate_random_id(), name=agent.name, user_id=current_user.id)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)

    # Initialize a new chat session
    genai.configure(api_key=os.getenv("API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat_session = model.start_chat(history=[])

    new_chat_session = models.ChatSession(agent_id=db_agent.id, chat_id=chat_session.id)
    db.add(new_chat_session)
    db.commit()

    return db_agent

@router.get("/agents/{agent_id}", response_model=schemas.Agent)
def read_agent(agent_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None or db_agent.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent