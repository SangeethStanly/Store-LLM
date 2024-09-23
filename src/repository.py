import json
import re
from sqlalchemy import text
from .redis_repository import load_memory_from_redis, save_memory_to_redis
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from .constants import db_information, sql_generation_template, sql_generation_with_history_template, common_instructions_for_query_generation
from .database import sql_db


def load_schema(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def cursor_result_to_string(result):
    result_string = ""
    for row in result:
        result_string += str(row) + "\n"
    return result_string


def map_qa(history):
    # Use regex to capture each "Human" question and its corresponding "AI" response
    pattern = r'Human:\s*(.*?)\nAI:\s*(.*?)(?=\nHuman:|\Z)'

    matches = re.findall(pattern, history, re.DOTALL)

    # Create a dictionary where the questions (Human) are keys and responses (AI) are values
    qa_dict = {human.strip().lower(): ai.strip() for human, ai in matches}

    return qa_dict


def query_response(response):
    response_content = response.strip()
    if (response_content.startswith('```sql') and response_content.endswith('```')):
        return True
    else:
        return False


def query_to_result(response):
    if query_response(response.content):
        sql_query = response.content.strip('```sql').strip('```')
        query_result = sql_db.run(text(sql_query))
        # query_result = cursor_result_to_string(query_result)
        print(query_result)
        return sql_query, query_result
    else:
        sql_query = None
        query_result = None
        return sql_query, query_result


def final_prompt_with_history(question, history):
    qa_dict = {}
    if history['history']:
        qa_dict = map_qa(history['history'])
    template = sql_generation_with_history_template
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
            return {"ai_response": response}

    system_message_prompt_template = SystemMessagePromptTemplate.from_template(
        template)
    human_template = f"{question}"
    human_message_prompt_template = HumanMessagePromptTemplate.from_template(
        human_template)
    chat_prompt_template = ChatPromptTemplate.from_messages(
        [system_message_prompt_template, human_message_prompt_template])
    prompt = chat_prompt_template.format_prompt(history=qa_dict, schema=schema, db_info=db_info, instructions=instructions,
                                                question=question).to_messages()
    return {"propmt": prompt}


def prompt_without_history(question):
    template = sql_generation_template
    prompt_template = PromptTemplate.from_template(template=template)
    schema = json.dumps(load_schema("db_schema.json"), indent=4)
    db_info = db_information
    instructions = common_instructions_for_query_generation

    prompt = prompt_template.format(
        question=question, schema=schema, db_info=db_info, instructions=instructions)
    return {"prompt": prompt}
