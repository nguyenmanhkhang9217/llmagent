from pydantic import BaseModel
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    agents: List["Agent"] = []

    class Config:
        from_attributes = True

class AgentBase(BaseModel):
    name: str

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    prompt: str
    agent_id: str

class ChatResponse(BaseModel):
    response: str

class ChatHistoryResponse(BaseModel):
    messages: List[str]
    responses: List[str]
