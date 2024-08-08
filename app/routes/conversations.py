from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from llm import LLMAgent
from models import Agent
from dependencies import get_db
from config import llm_types

router = APIRouter()
agent = LLMAgent()

class ChatRequest(BaseModel):
    # agent_id: str
    user_input: str

@router.post("/agents/{agent_id}/chat/")
async def chat_with_agent(agent_id: str, request: ChatRequest, db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    response = agent.chat(llm_types, agent_id, request.user_input)
    return {"response": response}
