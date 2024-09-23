from src.redis_repository import load_memory_from_redis, save_memory_to_redis
from src.repository import final_prompt_with_history, prompt_without_history, query_to_result
from .ai_model import llm
from langchain.memory import ConversationBufferMemory


def prompt_builder(state):
    question = state.get('question', '').strip()
    history = state.get('history', False)
    if history:
        session_id = state.get('session_id', None)
        memory = load_memory_from_redis(
            session_id) or ConversationBufferMemory()
        history = memory.load_memory_variables({})
        prompt_or_response = final_prompt_with_history(question, history)
        ai_response = prompt_or_response.get('ai_response', None)
        prompt = prompt_or_response.get('prompt', None)
        if not prompt:
            ai_response = prompt_or_response.get('ai_response', None)
            if ai_response:
                return {"ai_response": ai_response}
            else:
                prompt = prompt_without_history(question)
    else:
        prompt = prompt_without_history(question)

    return {"prompt": prompt}


def invoke_llm_and_execute(state):
    prompt = state.get('prompt', '')
    response = llm.invoke(prompt["prompt"])

    sql_query, query_result = query_to_result(response)
    response_dict = {"prompt": prompt,
                     "query_generated": sql_query, "result": query_result or response.content}

    return {"response_dict": response_dict}


def improvise_result_format(state):
    response_dict = state.get('response_dict', None)
    question = state.get('question', '')
    history = state.get('history', None)
    session_id = state.get('session_id', None)
    if response_dict:
        result_generation_prompt = str(
            response_dict) + ". Based on the dict provided, create a textual response. If the query_result is empty, don't hallucinate. Just give the rsponse as failed to execute the query."
        ai_response = llm.invoke(result_generation_prompt)
        response = ai_response.content

        if history:
            memory = load_memory_from_redis(
                session_id) or ConversationBufferMemory()
            memory.save_context({"input": question}, {
                "output": response})

            save_memory_to_redis(session_id, memory)

        return {"ai_response": response}

    else:
        return {"ai_response": "Sorry, unable to process the request"}


def final_response(state):
    ai_response = state.get('ai_response', None)
    return {"ai_response": ai_response}
