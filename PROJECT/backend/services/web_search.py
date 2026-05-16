"""
Web Search Service — fetches real-time market data via DuckDuckGo.
Used by agents to enrich analysis with live web intelligence.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from duckduckgo_search import DDGS

from backend.config import settings

# Thread pool for running synchronous search without blocking the event loop
executor = ThreadPoolExecutor(max_workers=10)

async def search_market_data(query: str, max_results: int = None) -> list[dict]:
    """
    Search the web for market-related information asynchronously.
    Uses a thread pool to avoid blocking the event loop.
    """
    if max_results is None:
        max_results = settings.search_max_results

    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(executor, _execute_search, query, max_results)
    except Exception:
        return []


def _execute_search(query: str, max_results: int) -> list[dict]:
    """Synchronous search execution for the thread pool."""
    results = []
    with DDGS() as ddgs:
        # DDGS().text returns a generator of dicts
        search_results = ddgs.text(query, max_results=max_results)
        for r in search_results:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            })
    return results


async def search_competitors(niche: str) -> list[dict]:
    """Search for existing competitors in a niche."""
    query = f"{niche} competitors market leaders startups 2025"
    return await search_market_data(query)


async def search_trends(topic: str) -> list[dict]:
    """Search for current trends related to a topic."""
    query = f"{topic} market trends growth opportunities 2025"
    return await search_market_data(query)


async def search_sentiment(product_idea: str) -> list[dict]:
    """Search for public sentiment about a product concept."""
    query = f"{product_idea} user reviews opinions demand pain points"
    return await search_market_data(query)


def format_search_results_for_llm(results: list[dict]) -> str:
    """
    Format search results into a readable string for the LLM to consume.
    Keeps it concise to avoid token bloat.
    """
    if not results:
        return "No web results found."

    formatted_lines = []
    for i, result in enumerate(results, 1):
        title = result.get("title", "Untitled")
        snippet = result.get("snippet", "No description")
        url = result.get("url", "")
        formatted_lines.append(
            f"[{i}] {title}\n    {snippet}\n    Source: {url}"
        )

    return "\n\n".join(formatted_lines)
