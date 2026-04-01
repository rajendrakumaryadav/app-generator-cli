"""
Tool registry — add your custom tools here and they are automatically
bound to the AssistantAgent.
"""
from __future__ import annotations

from langchain_core.tools import BaseTool

from app.tools.search import web_search_tool


def get_tools() -> list[BaseTool]:
    """Return all tools available to the agent."""
    return [
        web_search_tool,
        # Add more tools here, e.g.:
        # calculator_tool,
        # retriever_tool,
    ]
