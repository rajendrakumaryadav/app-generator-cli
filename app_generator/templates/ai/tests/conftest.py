"""Shared test fixtures for the AI application."""
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_openai():
    """Patch ChatOpenAI so tests never hit the real API."""
    with patch("langchain_openai.ChatOpenAI") as mock_cls:
        instance = mock_cls.return_value
        instance.ainvoke = AsyncMock(return_value=_fake_message("Test response"))
        instance.bind_tools = lambda tools: instance
        yield instance


def _fake_message(content: str):
    from langchain_core.messages import AIMessage
    msg = AIMessage(content=content)
    msg.tool_calls = []
    return msg
