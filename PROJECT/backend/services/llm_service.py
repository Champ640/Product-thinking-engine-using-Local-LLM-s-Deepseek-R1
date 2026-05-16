"""
LLM Service — communicates with Ollama/Qwen3.
Handles streaming, thinking mode, and conversation history.
"""

import json
from typing import AsyncGenerator

import httpx

from backend.config import settings


OLLAMA_CHAT_URL = f"{settings.ollama_base_url}/api/chat"


async def stream_chat(
    messages: list[dict],
    use_thinking: bool = True,
) -> AsyncGenerator[dict, None]:
    """
    Stream a chat response from Ollama token-by-token.

    Yields dicts with keys:
      - "type": "thinking" | "content" | "done"
      - "text": the token text (empty for "done")

    The /think or /no_think directive is appended to the last
    user message to control Qwen3's reasoning mode.
    """
    prepared_messages = _prepare_messages(messages, use_thinking)
    temperature = (
        settings.ollama_thinking_temp if use_thinking
        else settings.ollama_normal_temp
    )

    payload = {
        "model": settings.ollama_model,
        "messages": prepared_messages,
        "stream": True,
        "options": {
            "temperature": temperature,
            "top_p": 0.95 if use_thinking else 0.8,
            "top_k": 20,
        },
    }

    buffer = ""
    inside_think_block = False

    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream("POST", OLLAMA_CHAT_URL, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue

                chunk = json.loads(line)
                token = chunk.get("message", {}).get("content", "")

                if not token:
                    if chunk.get("done"):
                        if buffer:
                            yield {"type": "thinking" if inside_think_block else "content", "text": buffer}
                            buffer = ""
                        yield {"type": "done", "text": ""}
                    continue

                buffer += token
                parts, buffer, inside_think_block = _parse_think_buffer(buffer, inside_think_block)
                for part in parts:
                    yield part

                if chunk.get("done"):
                    if buffer:
                        yield {"type": "thinking" if inside_think_block else "content", "text": buffer}
                        buffer = ""
                    yield {"type": "done", "text": ""}


async def chat(
    messages: list[dict],
    use_thinking: bool = True,
) -> dict:
    """
    Non-streaming chat — collects full response.

    Returns dict with:
      - "thinking": str (the reasoning trace)
      - "content": str (the final answer)
    """
    thinking_parts = []
    content_parts = []

    async for token in stream_chat(messages, use_thinking):
        if token["type"] == "thinking":
            thinking_parts.append(token["text"])
        elif token["type"] == "content":
            content_parts.append(token["text"])

    return {
        "thinking": "".join(thinking_parts),
        "content": "".join(content_parts),
    }


async def check_ollama_health() -> bool:
    """Check if Ollama server is reachable."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(settings.ollama_base_url)
            return resp.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def _prepare_messages(
    messages: list[dict],
    use_thinking: bool,
) -> list[dict]:
    """
    Append /think or /no_think to the last user message
    to control Qwen3's reasoning mode.
    """
    if not messages:
        return messages

    prepared = [msg.copy() for msg in messages]
    directive = " /think" if use_thinking else " /no_think"

    # Find last user message and append directive
    for i in range(len(prepared) - 1, -1, -1):
        if prepared[i].get("role") == "user":
            prepared[i]["content"] = prepared[i]["content"] + directive
            break

    return prepared


def _parse_think_buffer(buffer: str, inside_think_block: bool) -> tuple[list[dict], str, bool]:
    """
    Stateful parser for token streams that might split <think> tags.
    Returns (yieldable_parts, remaining_buffer, inside_think_block_state)
    """
    parts = []

    while True:
        if not inside_think_block:
            idx = buffer.find("<think>")
            if idx != -1:
                if idx > 0:
                    parts.append({"type": "content", "text": buffer[:idx]})
                buffer = buffer[idx + len("<think>"):]
                inside_think_block = True
            else:
                break
        else:
            idx = buffer.find("</think>")
            if idx != -1:
                if idx > 0:
                    parts.append({"type": "thinking", "text": buffer[:idx]})
                buffer = buffer[idx + len("</think>"):]
                inside_think_block = False
            else:
                break

    target = "</think>" if inside_think_block else "<think>"
    split_idx = -1

    for i in range(1, len(target)):
        if buffer.endswith(target[:i]):
            split_idx = len(buffer) - i
            break

    if split_idx != -1:
        safe_part = buffer[:split_idx]
        buffer = buffer[split_idx:]
        if safe_part:
            parts.append({
                "type": "thinking" if inside_think_block else "content",
                "text": safe_part
            })
    else:
        if buffer:
            parts.append({
                "type": "thinking" if inside_think_block else "content",
                "text": buffer
            })
            buffer = ""

    return parts, buffer, inside_think_block
