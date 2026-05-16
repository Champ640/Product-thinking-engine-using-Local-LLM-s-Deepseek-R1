"""
PRODUCT THINKER — FastAPI Application Entry Point.
Serves the frontend, handles WebSocket chat, and exposes REST endpoints.
"""

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse

from backend.config import settings
from backend.services.llm_service import check_ollama_health
from backend.agents.pipeline import run_pipeline
from backend.prompts.system_prompts import OCCUPATION_PROMPTS


app = FastAPI(
    title="PRODUCT THINKER",
    description="AI-Powered Product Ideation & Market Intelligence",
    version="1.0.0",
)

# Store active session plans in memory
session_plans: dict[str, str] = {}

# Paths
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


# --- REST Endpoints ---

@app.get("/api/occupations")
async def get_occupations():
    """Return the list of available occupations."""
    occupations = [
        {"id": "software-developer", "label": "Software Developer", "icon": "💻"},
        {"id": "designer", "label": "Designer", "icon": "🎨"},
        {"id": "marketing", "label": "Marketing / Growth", "icon": "📈"},
        {"id": "finance", "label": "Finance / Accounting", "icon": "💰"},
        {"id": "healthcare", "label": "Healthcare Professional", "icon": "🏥"},
        {"id": "educator", "label": "Educator / Teacher", "icon": "📚"},
        {"id": "content-creator", "label": "Content Creator / Writer", "icon": "✍️"},
        {"id": "ecommerce", "label": "E-Commerce / Retail", "icon": "🛒"},
        {"id": "freelancer", "label": "Freelancer / Consultant", "icon": "🧑‍💼"},
        {"id": "student", "label": "Student / Researcher", "icon": "🎓"},
        {"id": "other", "label": "Other", "icon": "✏️"},
    ]
    return {"occupations": occupations}


@app.get("/api/health")
async def health_check():
    """Check if Ollama is reachable."""
    ollama_healthy = await check_ollama_health()
    return {
        "status": "ok" if ollama_healthy else "degraded",
        "ollama": ollama_healthy,
        "model": settings.ollama_model,
    }


@app.get("/api/plan/{session_id}")
async def get_plan(session_id: str):
    """Download a generated plan as Markdown."""
    plan = session_plans.get(session_id)
    if not plan:
        return PlainTextResponse("Plan not found", status_code=404)

    return PlainTextResponse(
        plan,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="product-thinker-plan.md"'
        },
    )


# --- WebSocket Chat ---

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    Main chat WebSocket endpoint.

    Protocol:
      Client → Server:
        {"type": "start", "occupation": "...", "idea": "..."}
        {"type": "chat", "message": "..."}

      Server → Client:
        {"type": "stage", "stage": "...", "label": "..."}
        {"type": "thinking", "content": "..."}
        {"type": "content", "content": "..."}
        {"type": "info", "content": "..."}
        {"type": "stage_complete", "stage": "..."}
        {"type": "plan_ready", "content": "...", "session_id": "..."}
        {"type": "error", "message": "..."}
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type")

            if msg_type == "start":
                await _handle_start(websocket, data, session_id)
            elif msg_type == "chat":
                await _handle_follow_up(websocket, data, session_id)
            else:
                await _send_ws(websocket, {
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                })

    except WebSocketDisconnect:
        pass
    except json.JSONDecodeError:
        await _send_ws(websocket, {
            "type": "error",
            "message": "Invalid JSON message",
        })
    except Exception as e:
        await _send_ws(websocket, {
            "type": "error",
            "message": f"Server error: {str(e)}",
        })


async def _handle_start(websocket: WebSocket, data: dict, session_id: str):
    """Handle a pipeline start request."""
    occupation = data.get("occupation", "Other")
    idea = data.get("idea", "")

    if not idea.strip():
        await _send_ws(websocket, {
            "type": "error",
            "message": "Please provide a product idea.",
        })
        return

    # Check Ollama health first
    if not await check_ollama_health():
        await _send_ws(websocket, {
            "type": "error",
            "message": (
                "Cannot reach Ollama. Please ensure it's running "
                f"at {settings.ollama_base_url} with model "
                f"{settings.ollama_model} pulled."
            ),
        })
        return

    # Create a send function that forwards to WebSocket
    async def send_message(msg: dict):
        await _send_ws(websocket, msg)

    # Run the full pipeline
    results = await run_pipeline(
        occupation=occupation,
        idea=idea,
        send_message=send_message,
    )

    # Store the plan for download
    plan = results.get("plan", "")
    session_plans[session_id] = plan

    # Notify client the plan is downloadable
    await _send_ws(websocket, {
        "type": "plan_ready",
        "content": plan,
        "session_id": session_id,
    })


async def _handle_follow_up(websocket: WebSocket, data: dict, session_id: str):
    """Handle a follow-up chat message after pipeline completion."""
    from backend.services import llm_service

    message = data.get("message", "")
    if not message.strip():
        return

    plan_context = session_plans.get(session_id, "")
    messages = [
        {
            "role": "system",
            "content": (
                "You are PRODUCT THINKER. The user has already received "
                "their MVP plan. Help them refine specific parts. "
                "Here is their current plan:\n\n" + plan_context[:3000]
            ),
        },
        {"role": "user", "content": message},
    ]

    async for token in llm_service.stream_chat(messages, use_thinking=False):
        if token["type"] == "done":
            continue
        await _send_ws(websocket, {
            "type": token["type"],
            "content": token["text"],
        })

    await _send_ws(websocket, {"type": "response_complete"})


async def _send_ws(websocket: WebSocket, data: dict):
    """Send a JSON message via WebSocket with error handling."""
    try:
        await websocket.send_text(json.dumps(data))
    except Exception:
        pass


# --- Static Files (Frontend) ---

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)


# Mount static assets
if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
