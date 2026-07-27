import pytest
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import AIMessage
from core.graph.research.search_agent import search_agent
from core.graph.research.writer_agent import writer_agent


@pytest.mark.asyncio
async def test_search_agent_returns_command():
    state = {"question": "Obscure Query", "messages": []}
    res = await search_agent(state)
    assert res.goto == "supervisor"
    assert "search_results" in res.update


@pytest.mark.asyncio
async def test_writer_agent_returns_command():
    state = {"question": "Obscure Query", "search_results": "No reliable search results found.", "messages": []}
    res = await writer_agent(state)
    assert res.goto == "supervisor"
    assert "draft" in res.update
