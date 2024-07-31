from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Agent, AgentCreate, AgentResponse
from agent_manager import AgentManager
from dependencies import get_db, generate_random_id
import schemas, auth

router = APIRouter()
agent_manager = AgentManager()


@router.post("/agents/")
def create_agent(agent: AgentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    id = generate_random_id()
    db_agent = Agent(id=id, name=agent.name, user_id=current_user.id, description=agent.description)
    try:
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        return {"response": 'created'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}", response_model=AgentResponse)
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent
