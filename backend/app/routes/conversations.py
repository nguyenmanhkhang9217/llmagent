from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from agent_manager import AgentManager
from models import Agent
from dependencies import get_db

router = APIRouter()
agent_manager = AgentManager()

class ChatRequest(BaseModel):
    # agent_id: str
    user_input: str

@router.post("/agents/{agent_id}/chat/")
async def chat_with_agent(agent_id: int, request: ChatRequest, db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    response = agent_manager.chat_with_agent(agent_id, request.user_input)
    return {"response": response}
