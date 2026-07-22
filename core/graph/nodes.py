# ============================================================
# core/graph/nodes.py — LangGraph Node Functions
# ============================================================
# TODO: Define `chat_node` — call LLM with current state
# TODO: Define `tool_node` — execute selected tool
# TODO: Define `memory_node` — load/save memory & summaries
# TODO: Define `rag_node` — retrieve relevant documents
# TODO: Define `planner_node` — break task into sub-steps
# TODO: Define `error_node` — handle and format errors
# ============================================================


from shared.logger import logger
from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool
from core.graph.state import GraphState
from core.llm.manager import LLMManager


def create_chatbot_node(
    llm: LLMManager,
    tools: list[BaseTool],
):
    tool_enabled_llm = llm.bind_tools(tools)

    async def chatbot_node(
        state: GraphState,
    ):
        messages = state["messages"]
        response = await tool_enabled_llm.ainvoke(messages)
        logger.debug("Content: %s", response.content)
        logger.debug("Tool Calls: %s", response.tool_calls)
        return {
            "messages": [
                response,
            ]
        }

    return chatbot_node


def create_refiner_node(
    llm: LLMManager,
):
    async def refiner_node(
        state: GraphState,
    ):
        messages = state["messages"]
        from langchain_core.messages import SystemMessage
        
        system_prompt = SystemMessage(content="You are an expert assistant and editor. Based on the conversation history and any tool results, provide a clear, accurate, and highly polished final answer. Do not repeat words endlessly. Stop when your thought is complete.")
        
        prompt = [system_prompt] + messages
        
        response = await llm.ainvoke(prompt)
        logger.debug("Refined Content: %s", response.content)
        return {
            "messages": [
                AIMessage(content=response.content, name="refiner"),
            ]
        }

    return refiner_node
