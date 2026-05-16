"""
Brainstorm Agent — Stage 1 of the pipeline.
Takes user's occupation and rough idea, generates 10 refined product ideas.
"""

from backend.services import llm_service
from backend.prompts.stage_prompts import BRAINSTORM_PROMPT
from backend.prompts.system_prompts import get_system_prompt


async def run(occupation: str, idea: str, on_token=None) -> dict:
    """
    Run the brainstorming stage.

    Args:
        occupation: User's occupation
        idea: User's rough product idea
        on_token: Optional async callback for streaming tokens

    Returns:
        dict with "thinking" and "content" keys
    """
    system_prompt = get_system_prompt(occupation)
    user_prompt = BRAINSTORM_PROMPT.format(
        occupation=occupation,
        idea=idea,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    if on_token:
        return await _run_streaming(messages, on_token)

    return await llm_service.chat(messages, use_thinking=True)


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
