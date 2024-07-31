from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    description = Column(Text)
    # chat_sessions = relationship("ChatSession", back_populates="agent")

# class UserFile(Base):
#     __tablename__ = 'user_files'
#     id = Column(Integer, primary_key=True, index=True)
#     agent_id = Column(Integer, ForeignKey('agents.id'))
#     file_path = Column(String)
#     # agent = relationship("Agent", back_populates="files")

class AgentCreate(BaseModel):
    name: str
    description: str

class AgentResponse(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True
