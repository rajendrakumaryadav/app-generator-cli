"""
AssistantAgent — a simple LangGraph ReAct agent wired to the configured LLM.

Extend this class to add memory, tools, and custom graph nodes.
"""
from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph

from app.config import settings
from app.tools.registry import get_tools


class AssistantAgent:
    """A LangGraph-powered conversational agent."""

    SYSTEM_PROMPT = (
        "You are a helpful, concise, and accurate assistant. "
        "Use the available tools when appropriate. "
        "If you don't know something, say so honestly."
    )

    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.2,
        )
        self._tools = get_tools()
        self._llm_with_tools = self._llm.bind_tools(self._tools)
        self._graph = self._build_graph()

    # ------------------------------------------------------------------ #
    #  Public
    # ------------------------------------------------------------------ #

    async def invoke(self, user_message: str, history: list[dict[str, str]] | None = None) -> str:
        """Run the agent and return the assistant's reply."""
        messages = [SystemMessage(content=self.SYSTEM_PROMPT)]

        for msg in (history or []):
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            # assistant messages are added by LangGraph internally

        messages.append(HumanMessage(content=user_message))

        result = await self._graph.ainvoke({"messages": messages})
        return result["messages"][-1].content  # type: ignore[index]

    # ------------------------------------------------------------------ #
    #  Graph construction
    # ------------------------------------------------------------------ #

    def _build_graph(self) -> Any:
        """Build a minimal ReAct graph: call model → maybe call tools → end."""
        builder = StateGraph(MessagesState)

        builder.add_node("agent", self._call_model)
        builder.add_node("tools", self._call_tools)

        builder.add_edge(START, "agent")
        builder.add_conditional_edges("agent", self._should_use_tools)
        builder.add_edge("tools", "agent")

        return builder.compile()

    async def _call_model(self, state: MessagesState) -> dict[str, Any]:
        response = await self._llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    async def _call_tools(self, state: MessagesState) -> dict[str, Any]:
        from langchain_core.messages import ToolMessage

        last_message = state["messages"][-1]
        tool_map = {t.name: t for t in self._tools}
        results = []

        for tool_call in last_message.tool_calls:  # type: ignore[attr-defined]
            tool = tool_map.get(tool_call["name"])
            if tool is None:
                output = f"Error: unknown tool '{tool_call['name']}'"
            else:
                output = await tool.ainvoke(tool_call["args"])
            results.append(
                ToolMessage(content=str(output), tool_call_id=tool_call["id"])
            )

        return {"messages": results}

    @staticmethod
    def _should_use_tools(state: MessagesState) -> str:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:  # type: ignore[attr-defined]
            return "tools"
        return END
