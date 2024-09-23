from langgraph.graph import StateGraph, END

from src.node import final_response, improvise_result_format, invoke_llm_and_execute, prompt_builder

from .schemas import GraphState

workflow = StateGraph(GraphState)

workflow.add_node("build_prompt", prompt_builder)
workflow.add_node("query_generator", invoke_llm_and_execute)
workflow.add_node("result_improviser", improvise_result_format)
workflow.add_node("final_response", final_response)


def direct_response_or_query(state):
    ai_response = state.get('ai_response', None)
    prompt = state.get('prompt', None)
    if ai_response:
        return "final_response"
    elif prompt:
        return "query_generator"


workflow.add_conditional_edges(
    "build_prompt",
    direct_response_or_query,
    {
        "final_response": "final_response",
        "query_generator": "query_generator"
    }
)

workflow.set_entry_point("build_prompt")
workflow.add_edge('query_generator', 'result_improviser')
workflow.add_edge('result_improviser', 'final_response')
workflow.add_edge('final_response', END)
