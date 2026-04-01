"""
Example tool: simple web search stub.

Replace the implementation with a real provider such as:
- Tavily:  `pip install langchain-tavily`
- SerpAPI: `pip install google-search-results`
- DuckDuckGo: `pip install duckduckgo-search`
"""
from langchain_core.tools import tool


@tool
async def web_search_tool(query: str) -> str:
    """Search the web for up-to-date information on a given query.

    Args:
        query: The search query string.

    Returns:
        A string summarising the top search results.
    """
    # ── Stub — replace with a real search provider ──────────────────────
    # Example using Tavily (recommended for LangChain agents):
    #
    #   from langchain_community.tools.tavily_search import TavilySearchResults
    #   search = TavilySearchResults(max_results=3)
    #   results = await search.ainvoke({"query": query})
    #   return "\n".join(r["content"] for r in results)
    #
    # ────────────────────────────────────────────────────────────────────
    return (
        f"[web_search stub] No live results for '{query}'. "
        "Configure a real search provider in app/tools/search.py."
    )
