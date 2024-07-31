from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Agent, AgentCreate, AgentResponse
from agent_manager import AgentManager
from dependencies import get_db

router = APIRouter()
agent_manager = AgentManager()


@router.post("/agents/", response_model=AgentResponse)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    db_agent = Agent(name=agent.name, description=agent.description)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("/agents/{agent_id}", response_model=AgentResponse)
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent
