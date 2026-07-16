from langgraph.graph import StateGraph
from langgraph.graph import START, END

from core.graph.nodes import create_chatbot_node
from core.graph.state import GraphState
from core.llm.manager import LLMManager


class GraphBuilder:
    def __init__(self, llm: LLMManager):
        self._llm  = llm

    def build(self):
        # 1. Create StateGraph
        builder = StateGraph(GraphState)

        # 2. Add chatbot node
        builder.add_node("chatbot", create_chatbot_node(self._llm))

        # 3. Connect START -> chatbot
        builder.add_edge(START, "chatbot")

        # 4. Connect chatbot -> END
        builder.add_edge("chatbot", END)

        # 5. Compile
        graph = builder.compile()
        # 6. Return compiled graph
        return graph
