import json
from .schemas import Prompt, SessionPrompt
from fastapi import APIRouter, Depends
from .ai_model import llm
from .database import get_db
from .repository import load_schema, map_qa, query_to_result
from .redis_repository import load_memory_from_redis, remove_session, save_memory_to_redis
from sqlalchemy.orm import Session
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from .agents import sql_agent_executor
from .constants import db_information, sql_generation_template, sql_generation_with_history_template, common_instructions_for_query_generation
from .graph import workflow

router = APIRouter(prefix="/store")


@router.post("/info")
async def info(
    request: Prompt
):
    question = request.question
    graph = workflow.compile()
    result = graph.invoke({"question": question})
    return {"data": result.get('ai_response', None)}


@router.post("/product_info_history")
async def product_info(request: SessionPrompt):
    session_id = request.session_id
    question = request.question
    graph = workflow.compile()
    result = graph.invoke(
        {"question": question, "session_id": session_id, "history": True})

    return {"data": result.get('ai_response', None)}


@router.post("/integrated_db")
async def integrated_db(request: Prompt):
    question = request.question
    result = sql_agent_executor.run(question)
    print(result)
    return {"Response": "Success"}


@router.delete("/clear_session/{session_id}")
async def clear_session_data(session_id: int):
    # Find all keys related to the session_id
    response = remove_session(session_id)

    return {"message": response}
