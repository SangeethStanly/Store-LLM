import json
import re
import langchain
from sqlalchemy import text


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


def query_to_result(response, db):
    if query_response(response.content):
        sql_query = response.content.strip('```sql').strip('```')
        query_result = db.execute(text(sql_query))
        query_result = cursor_result_to_string(query_result)
        return sql_query, query_result
    else:
        sql_query = None
        query_result = None
        return sql_query, query_result
