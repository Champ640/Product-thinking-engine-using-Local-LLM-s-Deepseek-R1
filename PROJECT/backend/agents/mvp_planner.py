"""
MVP Planner Agent — Stage 4 of the pipeline.
Produces a comprehensive, actionable MVP blueprint.
"""

from backend.services import llm_service
from backend.services.web_search import (
    search_market_data,
    format_search_results_for_llm,
)
from backend.prompts.stage_prompts import MVP_PROMPT
from backend.prompts.system_prompts import get_system_prompt


async def run(
    occupation: str,
    idea: str,
    brainstorm_results: str,
    sentiment_results: str,
    niche_results: str,
    on_token=None,
) -> dict:
    """
    Run the MVP planning stage.

    Searches for tech stack and pricing intelligence,
    then generates a complete MVP plan.
    """
    web_results = await _gather_tech_data(idea, niche_results)
    web_data_text = format_search_results_for_llm(web_results)

    # Summarize previous stages to stay within context
    brainstorm_summary = _summarize(brainstorm_results, max_chars=1000)
    sentiment_summary = _summarize(sentiment_results, max_chars=1000)

    system_prompt = get_system_prompt(occupation)
    user_prompt = MVP_PROMPT.format(
        occupation=occupation,
        idea=idea,
        niche_results=niche_results,
        brainstorm_summary=brainstorm_summary,
        sentiment_summary=sentiment_summary,
        web_data=web_data_text,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    if on_token:
        return await _run_streaming(messages, on_token)

    return await llm_service.chat(messages, use_thinking=True)


async def _gather_tech_data(idea: str, niche_results: str) -> list[dict]:
    """Search for tech stack and pricing reference data."""
    tech_results = await search_market_data(
        f"{idea} tech stack tools pricing SaaS"
    )
    pricing_results = await search_market_data(
        f"{idea} pricing model subscription freemium revenue"
    )
    return tech_results + pricing_results


def _summarize(text: str, max_chars: int = 1000) -> str:
    """Truncate text to stay within token limits."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... (truncated for brevity)"


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
