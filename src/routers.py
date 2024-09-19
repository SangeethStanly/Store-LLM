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

router = APIRouter(prefix="/store")


@router.post("/info")
async def info(
    request: Prompt,
    db: Session = Depends(get_db)
):
    template = sql_generation_template
    prompt_template = PromptTemplate.from_template(template=template)
    question = request.question
    schema = json.dumps(load_schema("db_schema.json"), indent=4)
    db_info = db_information
    instructions = common_instructions_for_query_generation

    prompt = prompt_template.format(
        question=question, schema=schema, db_info=db_info, instructions=instructions)
    response = llm.invoke(prompt)
    sql_query, query_result = query_to_result(response, db)

    response_dict = {"prompt": request.question,
                     "query_generated": sql_query, "query_result": query_result}

    result_generation_prompt = str(
        response_dict) + ". Based on the dict provided, create a textual response. If the query_result is empty, don't hallucinate. Just give the rsponse as failed to execute the query."

    result = llm.invoke(result_generation_prompt)

    return {"data": result.content}


@router.post("/product_info_history")
async def product_info(request: SessionPrompt,
                       db: Session = Depends(get_db)):
    session_id = request.session_id
    qa_dict = {}
    memory = load_memory_from_redis(session_id) or ConversationBufferMemory()
    history = memory.load_memory_variables({})
    if history['history']:
        qa_dict = map_qa(history['history'])
    template = sql_generation_with_history_template
    question = request.question
    schema = json.dumps(load_schema("db_schema.json"), indent=4)
    db_info = db_information
    instructions = common_instructions_for_query_generation + '\n' + f'''
        7. If a chat memory persist and the question doesn't require a new query, just use the information from memory and just use the mathematical functions and all if it is required to satisfy our question's answer.
        8. Also use the last question and response in the history to give answer. If the last message cannot give the answer for that question look the second last and so on.
        9. The query should be able to get the record using ILIKE.
    '''
    if qa_dict and question.strip().lower() in qa_dict:
        response = qa_dict[question.strip().lower()]
        if response:
            return {"data": query_result}

    system_message_prompt_template = SystemMessagePromptTemplate.from_template(
        template)
    human_template = f"{question}"
    human_message_prompt_template = HumanMessagePromptTemplate.from_template(
        human_template)
    chat_prompt_template = ChatPromptTemplate.from_messages(
        [system_message_prompt_template, human_message_prompt_template])
    final_prompt = chat_prompt_template.format_prompt(history=qa_dict, schema=schema, db_info=db_info, instructions=instructions,
                                                      question=question).to_messages()
    response = llm.invoke(final_prompt)

    sql_query, query_result = query_to_result(response, db)

    response_dict = {"prompt": request.question,
                     "query_generated": sql_query, "result": query_result or response.content}

    result_generation_prompt = str(
        response_dict) + ". Based on the dict provided, create a textual response. If the sql_query is None, just pass the result without hallucinating."

    result = llm.invoke(result_generation_prompt)

    memory.save_context({"input": question}, {
        "output": result.content})

    save_memory_to_redis(session_id, memory)

    return {"data": result.content}


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


# @router.get("/generate-schema")
# def generate_schema(db=Depends(get_db)):
#     schema = {"tables": {}}

#     # Get all table names
#     result = db.execute(text("""
#         SELECT table_name
#         FROM information_schema.tables
#         WHERE table_schema = 'public'
#         AND table_type = 'BASE TABLE';
#     """))
#     print("Query 1 result: ", result)
#     tables = [row[0] for row in result]
#     print("Table Results: ", tables)

#     # Get columns for each table
#     for table in tables:
#         result = db.execute(text("""
#             SELECT column_name
#             FROM information_schema.columns
#             WHERE table_schema = 'public'
#             AND table_name = :table_name;
#         """), {"table_name": table})
#         print("Query 2 result: ", result)

#         columns = [row[0] for row in result]
#         print("Columns Result: ", columns)
#         schema["tables"][table] = {"columns": columns}

#     # Save schema to a JSON file
#     with open("db_schema.json", "w") as f:
#         json.dump(schema, f, indent=4)

#     return {"message": "Database schema saved to db_schema.json"}
