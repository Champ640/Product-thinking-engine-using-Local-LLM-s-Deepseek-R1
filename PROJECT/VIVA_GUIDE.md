# PRODUCT THINKER 🧠 - Viva Preparation Guide

This guide is designed to help you prepare for a project Viva/Defense. It covers the core architecture, key technologies, workflow, and potential questions examiners might ask.

---

## 1. Project Overview
**PRODUCT THINKER** is an AI-powered product ideation and market intelligence system. It acts as an autonomous, multi-stage "product strategist," taking a rough user idea and running it through a sophisticated pipeline to produce a polished Minimum Viable Product (MVP) blueprint.

**Core Objective:** To help founders, creators, and professionals refine vague ideas into actionable, well-researched product plans using local, privacy-first AI.

---

## 2. Key Technologies (Tech Stack)

### Backend
*   **Python 3.10+**: The core programming language.
*   **FastAPI**: A modern, high-performance web framework used for serving the API, handling real-time WebSockets, and serving frontend files.
*   **Uvicorn**: An ASGI web server implementation for Python, used to run the FastAPI application.

### Frontend
*   **HTML5 / CSS3**: For the structure and styling. Uses custom, modern UI patterns (like the Stage Progress indicators and glassmorphism elements).
*   **Vanilla JavaScript**: No heavy frameworks (like React or Vue) were used. It relies on standard browser APIs, native WebSockets, and DOM manipulation to ensure high performance and a lightweight footprint.

### AI Engine & Pipeline
*   **Ollama**: A local LLM runner. It allows the project to run powerful AI models entirely on the user's machine without relying on paid APIs (like OpenAI) or compromising data privacy.
*   **DeepSeek R1 (deepseek-r1:1.5b)**: The specific Large Language Model used. It is a state-of-the-art reasoning model that uses `<think>` tags, allowing the system to output its "chain of thought" before providing the final answer.

---

## 3. Architecture & Key Components

The project is structured into modular components:

### A. The Agent Pipeline (`backend/agents/`)
Instead of a simple "chatbot," the system uses a chained, multi-agent pipeline. Each agent is responsible for a specific stage of the product ideation process:
1.  **Brainstorm Agent (`brainstorm.py`)**: Takes the user's raw idea and generates 10 refined, diverse product concepts.
2.  **Sentiment/Market Agent (`sentiment.py`)**: Analyzes the generated concepts for market demand, potential user sentiment, and feasibility.
3.  **Niche Finder Agent (`niche_finder.py`)**: Identifies the single best opportunity from the brainstormed ideas based on the sentiment analysis.
4.  **MVP Planner Agent (`mvp_planner.py`)**: Takes the winning idea and drafts a comprehensive, actionable MVP blueprint.
5.  **Pipeline Orchestrator (`pipeline.py`)**: Manages the flow of data between these agents and streams real-time updates back to the frontend.

### B. LLM Service (`backend/services/llm_service.py`)
Handles the direct communication with the Ollama server.
*   **Streaming**: It uses `httpx.AsyncClient` to stream responses token-by-token.
*   **Think Block Parsing**: It parses the incoming token stream to separate the model's `<think>...</think>` reasoning process from the actual user-facing content, allowing the UI to display "Thinking..." states.

### C. Real-Time Communication (`backend/main.py` & `frontend/js/app.js`)
*   **WebSockets**: Used instead of standard HTTP POST requests because the AI generation process is slow and multi-staged. WebSockets allow the server to push real-time updates (e.g., "Stage 1 complete", token streams, error messages) instantly to the browser.

---

## 4. Potential Viva Questions & Answers

**Q: Why did you choose FastAPI over Flask or Django?**
> **A:** FastAPI was chosen because of its native and excellent support for asynchronous programming (`async/await`) and WebSockets. Since interacting with Local LLMs is an I/O-bound, time-consuming process, FastAPI ensures the server remains non-blocking and can stream data efficiently to the frontend.

**Q: Why use Ollama and a local model (DeepSeek R1) instead of the OpenAI API?**
> **A:** Local models offer three massive benefits: (1) **Privacy**: User ideas are highly confidential and never leave their machine. (2) **Cost**: It is 100% free to run locally, with no API token costs. (3) **Reasoning Transparency**: Using models that expose their `<think>` process allows us to build a more transparent AI that shows its work before concluding.

**Q: Explain how the real-time chat works in your project.**
> **A:** It uses WebSockets. When a user submits an idea, the frontend establishes a WebSocket connection with FastAPI. The FastAPI backend triggers the Agent Pipeline. As the LLM generates tokens, the backend immediately pushes these tokens over the WebSocket to the frontend, which dynamically updates the DOM.

**Q: What is the purpose of the different "Agents"?**
> **A:** Breaking the prompt into multiple agents (Brainstorm -> Sentiment -> Niche -> MVP) yields much higher quality results than asking an LLM to do everything in one prompt. Each agent has a specific system prompt and focus, and the output of one agent becomes the input of the next.

**Q: How do you handle the model's "thinking" process?**
> **A:** The `llm_service.py` has a specific parser (`_parse_think_tokens`) that detects `<think>` and `</think>` tags in the streaming response. It flags these tokens with a "thinking" type, allowing the frontend to hide or format the internal reasoning separately from the final answer.

**Q: What happens if Ollama isn't running?**
> **A:** The frontend has a `/api/health` polling mechanism. If Ollama isn't reachable, the UI displays a red offline indicator and prevents the user from starting the pipeline, showing a clear error message.

---

## 5. Tips for the Viva
*   **Demonstrate the live stream:** Examiners love seeing the text typing out in real-time. Emphasize that this is done via WebSockets, not simple HTTP requests.
*   **Show the Terminal:** Show them the backend terminal logs while it runs to prove that it is orchestrating multiple agents sequentially.
*   **Highlight the separation of concerns:** Mention how you separated the UI (Frontend), the API routing (`main.py`), the LLM logic (`llm_service.py`), and the business logic (`agents/`). This demonstrates good software engineering practices conforming to your `architecture.md` rules.
