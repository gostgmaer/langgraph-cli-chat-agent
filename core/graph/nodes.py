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
