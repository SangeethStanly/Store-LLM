from pydantic import BaseModel


class Prompt(BaseModel):
    question: str


class SessionPrompt(BaseModel):
    session_id: int
    question: str
