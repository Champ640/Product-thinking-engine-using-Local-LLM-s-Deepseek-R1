"""
Niche Finder Agent — Stage 3 of the pipeline.
Identifies the single best niche opportunity using competitor data.
"""

from backend.services import llm_service
from backend.services.web_search import (
    search_competitors,
    search_trends,
    format_search_results_for_llm,
)
from backend.prompts.stage_prompts import NICHE_PROMPT
from backend.prompts.system_prompts import get_system_prompt


async def run(
    occupation: str,
    idea: str,
    brainstorm_results: str,
    sentiment_results: str,
    on_token=None,
) -> dict:
    """
    Run the niche discovery stage.

    Searches for competitors and trends, then uses the LLM
    to identify the most promising niche and opportunity.
    """
    web_results = await _gather_competitor_data(idea)
    web_data_text = format_search_results_for_llm(web_results)

    system_prompt = get_system_prompt(occupation)
    user_prompt = NICHE_PROMPT.format(
        occupation=occupation,
        idea=idea,
        brainstorm_results=brainstorm_results,
        sentiment_results=sentiment_results,
        web_data=web_data_text,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    if on_token:
        return await _run_streaming(messages, on_token)

    return await llm_service.chat(messages, use_thinking=True)


async def _gather_competitor_data(idea: str) -> list[dict]:
    """Collect competitor and trend data from the web."""
    competitor_results = await search_competitors(idea)
    trend_results = await search_trends(idea)
    return competitor_results + trend_results


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
