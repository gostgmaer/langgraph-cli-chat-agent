import pytest
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import AIMessage
from core.graph.research.search_agent import create_search_agent_node
from core.graph.research.writer_agent import create_writer_agent_node


@pytest.mark.asyncio
async def test_search_agent_empty_results():
    mock_llm = MagicMock()
    mock_bound_llm = AsyncMock()
    mock_bound_llm.ainvoke.return_value = AIMessage(content="")
    mock_llm.bind_tools.return_value = mock_bound_llm

    search_node = create_search_agent_node(mock_llm)
    state = {"question": "Obscure Query", "messages": []}
    res = await search_node(state)

    assert res["search_results"] == ""


@pytest.mark.asyncio
async def test_writer_fallback_on_empty_search():
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=AIMessage(content="Could not find sufficient data."))

    writer_node = create_writer_agent_node(mock_llm)
    state = {"question": "Obscure Query", "search_results": "", "messages": []}
    res = await writer_node(state)

    assert "Could not find" in res["draft"]
