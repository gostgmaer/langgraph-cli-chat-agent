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
            content=(
                "You are the assistant for this CLI app. Your actual capabilities are "
                "exactly these tools, nothing more -- if asked what you can do, describe "
                "these truthfully rather than inventing other skills or personas:\n"
                "- get_weather: current weather for a city\n"
                "- get_google_search: general web search\n"
                "- get_news: recent news on a topic\n"
                "- save_preference: remember a user preference (name, language, etc.)\n"
                "There is also a separate '/research <topic>' command (handled outside "
                "this chat turn) for deep, multi-step research with a search team -- "
                "mention it as an option for in-depth research questions.\n\n"
                f"Remembered user preferences: {preferences}. If the user shares a new "
                "preference, use the save_preference tool."
            )
        )
        
        formatted_messages = []
        for m in messages:
            if hasattr(m, "content") and isinstance(m.content, list):
                text_content = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in m.content)
                formatted_messages.append(type(m)(content=text_content))
            elif isinstance(m, dict) and isinstance(m.get("content"), list):
                text_content = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in m["content"])
                formatted_messages.append({**m, "content": text_content})
            else:
                formatted_messages.append(m)

        response = await tool_enabled_llm.ainvoke([sys_msg] + formatted_messages)
        
        logger.debug("Content: %s", response.content)
        logger.debug("Tool Calls: %s", response.tool_calls)
        
        state_update = {
            "messages": [response]
        }
        
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
