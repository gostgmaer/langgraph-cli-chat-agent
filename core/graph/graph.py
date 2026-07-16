from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langgraph.prebuilt import ToolNode

from core.graph.nodes import create_chatbot_node
from core.graph.state import GraphState
from core.llm.manager import LLMManager
from core.tools.news import get_news
from core.tools.search import get_google_search
from core.tools.weather import get_weather
from langgraph.prebuilt import tools_condition


class GraphBuilder:
    def __init__(self, llm: LLMManager):
        self._llm = llm

    def build(self):
        # 1. Create StateGraph
        builder = StateGraph(GraphState)

        # tools
        tools = [get_weather, get_google_search, get_news]
        # 2. Add chatbot node
        builder.add_node("chatbot", create_chatbot_node(self._llm, tools))
        # 2. Add Tool node

        builder.add_node(
            "tools",
            ToolNode(tools),
        )

        # 3. Connect START -> chatbot
        builder.add_edge(START, "chatbot")

        # 4. Connect chatbot -> END
        builder.add_conditional_edges("chatbot", tools_condition)

        builder.add_edge(
            "tools",
            "chatbot",
        )
        # 5. Compile
        graph = builder.compile()
        # 6. Return compiled graph
        return graph
