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
        preferences = state.get("user_preferences", {})
        
        from langchain_core.messages import SystemMessage
        sys_msg = SystemMessage(
            content=f"You are a helpful AI assistant. Remember and use the following user preferences: {preferences}. "
                    f"If the user shares a new preference (e.g. name, language, favorite color), use the save_preference tool."
        )
        
        response = await tool_enabled_llm.ainvoke([sys_msg] + messages)
        
        logger.debug("Content: %s", response.content)
        logger.debug("Tool Calls: %s", response.tool_calls)
        
        state_update = {
            "messages": [response]
        }
        
        # Intercept preference saving
        if hasattr(response, "tool_calls"):
            for tc in response.tool_calls:
                if tc["name"] == "save_preference":
                    key = tc["args"]["key"]
                    val = tc["args"]["value"]
                    if "user_preferences" not in state_update:
                        state_update["user_preferences"] = {}
                    state_update["user_preferences"][key] = val
                    
        return state_update

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
