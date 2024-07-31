from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import shutil
# from models import UserFile
from agent_manager import AgentManager
from models import Agent
from dependencies import get_db
import os

router = APIRouter()
agent_manager = AgentManager()
FILE_PATH = "files"
@router.post("/agents/{agent_id}/files/")
async def upload_file(agent_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    file_location = f"{FILE_PATH}/{agent_id}_{file.filename}"
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # user_file = UserFile(agent_id=agent_id, file_path=file_location)
    # db.add(user_file)
    # db.commit()
    # db.refresh(user_file)

    agent_manager.add_file_to_agent(agent_id, file_location)
    return {"filename": file_location}
