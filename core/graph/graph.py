from typing import Annotated, Any, Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.base import BaseCheckpointSaver
import operator

from core.graph.nodes import create_chatbot_node
from core.graph.research.graph import ResearchGraphBuilder
from core.graph.research.state import ResearchState
from core.llm.manager import LLMManager
from core.tools.news import get_news
from core.tools.search import get_google_search
from core.tools.weather import get_weather
from core.tools.preferences import save_preference
from core.graph.state import update_preferences


def _replace_list(left: list, right: list) -> list:
    """Replace reducer — new value fully replaces old (not append)."""
    return right if right is not None else left


class State(TypedDict, total=False):
    """Unified state schema combining Chat and Multi-Agent Research."""
    messages: Annotated[list[AnyMessage], add_messages]
    intent: str
    question: str
    sub_questions: Annotated[list[str], _replace_list]
    search_results: Annotated[list[str], _replace_list]
    revision_count: int
    draft: str
    final_answer: str
    user_preferences: Annotated[dict[str, Any], update_preferences]


def router_node(state: State) -> dict:
    """Classifies user input into standard chatbot vs research team."""
    if not state.get("messages"):
        return {"intent": "chat"}
    
    last_msg = state["messages"][-1]
    content = getattr(last_msg, "content", "")
    
    if isinstance(content, list):
        # Extract text from list of blocks (e.g. Gemini / Anthropic block structure)
        text_parts = [b.get("text", "") if isinstance(b, dict) else str(b) for b in content]
        text_content = "".join(text_parts).strip()
    else:
        text_content = str(content).strip()

    if text_content.startswith("/research "):
        topic = text_content[len("/research "):].strip()
        return {
            "intent": "research",
            "question": topic,
            # Hard-reset ALL research fields to prevent stale checkpoint state
            "sub_questions": [],
            "search_results": [],
            "draft": "",
            "revision_count": 0,
            "final_answer": "",
        }
    return {"intent": "chat"}


def route_decision(state: State) -> Literal["chatbot", "research_team"]:
    if state.get("intent") == "research":
        return "research_team"
    return "chatbot"


class GraphBuilder:
    """Builds a single master graph combining Router, Chatbot, Tools, and Research Subgraph."""

    def __init__(self, llm: LLMManager, checkpointer: BaseCheckpointSaver = None):
        self._llm = llm
        self._checkpointer = checkpointer

    def build(self):
        # 1. Subgraph: Research Team
        research_team_subgraph = ResearchGraphBuilder().build()

        # 2. Parent Graph
        builder = StateGraph(State)

        # 3. Add Nodes
        tools = [get_weather, get_google_search, get_news, save_preference]
        builder.add_node("router", router_node)
        builder.add_node("chatbot", create_chatbot_node(self._llm, tools))
        builder.add_node("tools", ToolNode(tools))
        builder.add_node("research_team", research_team_subgraph)

        # 4. Add Edges & Conditional Routing
        builder.add_edge(START, "router")
        builder.add_conditional_edges("router", route_decision)

        # Single-Agent Chat Branch
        builder.add_conditional_edges("chatbot", tools_condition)
        builder.add_edge("tools", "chatbot")

        # Multi-Agent Research Subgraph Branch
        builder.add_edge("research_team", END)

        if self._checkpointer:
            return builder.compile(checkpointer=self._checkpointer)
        return builder.compile()
