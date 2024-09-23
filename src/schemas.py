from pydantic import BaseModel
from typing import Dict, TypedDict, Optional


class GraphState(TypedDict):
    question: Optional[str] = None
    session_id: Optional[int] = None
    prompt: Optional[Dict] = None
    history: Optional[bool] = False
    response_dict: Optional[Dict] = None
    response: Optional[str] = None
    ai_response: Optional[Dict] = None


class Prompt(BaseModel):
    question: str


class SessionPrompt(BaseModel):
    session_id: int
    question: str
