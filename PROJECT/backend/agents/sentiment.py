"""
Sentiment Agent — Stage 2 of the pipeline.
Analyzes market sentiment for brainstormed ideas using web data.
"""

from backend.services import llm_service
from backend.services.web_search import (
    search_sentiment,
    search_market_data,
    format_search_results_for_llm,
)
from backend.prompts.stage_prompts import SENTIMENT_PROMPT
from backend.prompts.system_prompts import get_system_prompt


async def run(
    occupation: str,
    idea: str,
    brainstorm_results: str,
    on_token=None,
) -> dict:
    """
    Run the sentiment analysis stage.

    Searches the web for market sentiment around the top ideas,
    then uses the LLM to analyze demand, pain points, and gaps.
    """
    # Gather real-time web data
    web_results = await _gather_web_data(idea, brainstorm_results)
    web_data_text = format_search_results_for_llm(web_results)

    system_prompt = get_system_prompt(occupation)
    user_prompt = SENTIMENT_PROMPT.format(
        occupation=occupation,
        idea=idea,
        brainstorm_results=brainstorm_results,
        web_data=web_data_text,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    if on_token:
        return await _run_streaming(messages, on_token)

    return await llm_service.chat(messages, use_thinking=True)


async def _gather_web_data(idea: str, brainstorm_results: str) -> list[dict]:
    """Collect web search results for sentiment analysis."""
    # Search for the original idea's market reception
    results = await search_sentiment(idea)

    # Also search for general market data
    market_results = await search_market_data(
        f"{idea} market size demand growth"
    )
    results.extend(market_results)

    return results


async def _run_streaming(messages: list[dict], on_token) -> dict:
    """Stream tokens and collect full response."""
    thinking_parts = []
    content_parts = []

    async for token in llm_service.stream_chat(messages, use_thinking=True):
        if token["type"] == "done":
            continue

        await on_token(token)

        if token["type"] == "thinking":
            thinking_parts.append(token["text"])
        elif token["type"] == "content":
            content_parts.append(token["text"])

    return {
        "thinking": "".join(thinking_parts),
        "content": "".join(content_parts),
    }
