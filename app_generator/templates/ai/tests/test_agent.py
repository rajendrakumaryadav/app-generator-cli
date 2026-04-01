"""Tests for the AssistantAgent."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage


@pytest.mark.asyncio
async def test_agent_returns_string_response():
    """Agent.invoke() should return a plain string."""
    fake_ai_msg = AIMessage(content="Hello, I am your assistant!")
    fake_ai_msg.tool_calls = []  # no tool calls → goes straight to END

    with (
        patch("langchain_openai.ChatOpenAI") as mock_llm_cls,
        patch("app.tools.registry.get_tools", return_value=[]),
    ):
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(return_value=fake_ai_msg)
        mock_llm_cls.return_value = mock_llm

        from app.agents.assistant import AssistantAgent

        agent = AssistantAgent()
        result = await agent.invoke("Hello")

    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_agent_passes_history():
    """Agent should include prior history in the prompt."""
    fake_ai_msg = AIMessage(content="I remember!")
    fake_ai_msg.tool_calls = []

    with (
        patch("langchain_openai.ChatOpenAI") as mock_llm_cls,
        patch("app.tools.registry.get_tools", return_value=[]),
    ):
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(return_value=fake_ai_msg)
        mock_llm_cls.return_value = mock_llm

        from app.agents.assistant import AssistantAgent

        agent = AssistantAgent()
        history = [{"role": "user", "content": "My name is Alice"}]
        result = await agent.invoke("What is my name?", history=history)

    assert isinstance(result, str)
