from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langgraph.prebuilt import ToolNode
from core.graph.nodes import create_chatbot_node
from core.graph.state import GraphState
from core.llm.manager import LLMManager
from core.tools.news import get_news
from core.tools.search import get_google_search
from core.tools.weather import get_weather
from core.tools.preferences import save_preference
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.base import BaseCheckpointSaver

class GraphBuilder:
    def __init__(self, llm: LLMManager, checkpointer: BaseCheckpointSaver):
        self._llm = llm
        self._checkpointer = checkpointer

    def build(self):
        # 1. Create StateGraph
        builder = StateGraph(GraphState)

        # tools
        tools = [get_weather, get_google_search, get_news, save_preference]
        # 2. Add chatbot node
        builder.add_node("chatbot", create_chatbot_node(self._llm, tools))
        # 2. Add Tool node

        builder.add_node(
            "tools",
            ToolNode(tools),
        )

        # 3. Connect START -> chatbot
        builder.add_edge(START, "chatbot")

        # 4. Connect chatbot -> END or tools
        builder.add_conditional_edges("chatbot", tools_condition)

        builder.add_edge(
            "tools",
            "chatbot",
        )
        # 5. Compile
        # checkpointer = AsyncSqliteSaver()
        # builder.set_checkpointer(checkpointer)
        graph = builder.compile(checkpointer=self._checkpointer)
        # 6. Return compiled graph
        png = graph.get_graph().draw_mermaid_png()

        with open("graph.png", "wb") as f:
             f.write(png)

        print("Graph saved as graph.png")
        return graph
