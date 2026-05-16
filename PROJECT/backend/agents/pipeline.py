"""
Pipeline Orchestrator — runs all 4 agents in sequence.
Streams progress to the frontend via WebSocket callbacks.
"""

import json
from datetime import datetime

from backend.agents import brainstorm, sentiment, niche_finder, mvp_planner
from backend.services.plan_exporter import export_plan


# Stage definitions with display metadata
STAGES = [
    {"id": "brainstorm", "label": "🧠 Brainstorming Ideas", "color": "mint"},
    {"id": "sentiment", "label": "📊 Analyzing Sentiment", "color": "peach"},
    {"id": "niche", "label": "🔍 Finding Niches", "color": "lavender"},
    {"id": "mvp", "label": "📋 Building MVP Plan", "color": "sky"},
]


async def run_pipeline(
    occupation: str,
    idea: str,
    send_message,
) -> dict:
    """
    Execute the full 4-stage analysis pipeline.

    Args:
        occupation: User's occupation
        idea: User's rough product idea
        send_message: Async function to send WebSocket messages

    Returns:
        dict with all stage results and the final plan
    """
    results = {
        "occupation": occupation,
        "idea": idea,
        "timestamp": datetime.now().isoformat(),
        "stages": {},
    }

    # --- Stage 1: Brainstorm ---
    await send_message({
        "type": "stage",
        "stage": "brainstorm",
        "label": STAGES[0]["label"],
    })

    brainstorm_result = await brainstorm.run(
        occupation=occupation,
        idea=idea,
        on_token=lambda t: send_message({
            "type": t["type"],
            "content": t["text"],
        }),
    )
    results["stages"]["brainstorm"] = brainstorm_result

    await send_message({"type": "stage_complete", "stage": "brainstorm"})

    # --- Stage 2: Sentiment Analysis ---
    await send_message({
        "type": "stage",
        "stage": "sentiment",
        "label": STAGES[1]["label"],
    })

    await send_message({
        "type": "info",
        "content": "🌐 Searching the web for market data...",
    })

    sentiment_result = await sentiment.run(
        occupation=occupation,
        idea=idea,
        brainstorm_results=brainstorm_result["content"],
        on_token=lambda t: send_message({
            "type": t["type"],
            "content": t["text"],
        }),
    )
    results["stages"]["sentiment"] = sentiment_result

    await send_message({"type": "stage_complete", "stage": "sentiment"})

    # --- Stage 3: Niche Discovery ---
    await send_message({
        "type": "stage",
        "stage": "niche",
        "label": STAGES[2]["label"],
    })

    await send_message({
        "type": "info",
        "content": "🌐 Researching competitors and trends...",
    })

    niche_result = await niche_finder.run(
        occupation=occupation,
        idea=idea,
        brainstorm_results=brainstorm_result["content"],
        sentiment_results=sentiment_result["content"],
        on_token=lambda t: send_message({
            "type": t["type"],
            "content": t["text"],
        }),
    )
    results["stages"]["niche"] = niche_result

    await send_message({"type": "stage_complete", "stage": "niche"})

    # --- Stage 4: MVP Planning ---
    await send_message({
        "type": "stage",
        "stage": "mvp",
        "label": STAGES[3]["label"],
    })

    await send_message({
        "type": "info",
        "content": "🌐 Gathering tech stack and pricing data...",
    })

    mvp_result = await mvp_planner.run(
        occupation=occupation,
        idea=idea,
        brainstorm_results=brainstorm_result["content"],
        sentiment_results=sentiment_result["content"],
        niche_results=niche_result["content"],
        on_token=lambda t: send_message({
            "type": t["type"],
            "content": t["text"],
        }),
    )
    results["stages"]["mvp"] = mvp_result

    await send_message({"type": "stage_complete", "stage": "mvp"})

    # --- Generate plan.md ---
    plan_content = export_plan(results)
    results["plan"] = plan_content

    await send_message({
        "type": "plan_ready",
        "content": plan_content,
    })

    return results
