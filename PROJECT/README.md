# PRODUCT THINKER 🧠
> **Turn rough ideas into validated MVP plans with local AI.**

PRODUCT THINKER is an AI-powered product strategist that uses a multi-agent pipeline to brainstorm, analyze market sentiment, find niches, and draft comprehensive MVP blueprints—all running locally on your machine for 100% privacy and zero API costs.

![Screenshot](https://via.placeholder.com/800x450.png?text=Product+Thinker+UI) <!-- Add your real screenshot here! -->

## 🚀 Key Features
- **4-Stage Agent Pipeline**: Brainstorm → Sentiment Analysis → Niche Discovery → MVP Planning.
- **Local AI (Ollama)**: Uses **DeepSeek R1** for transparent, "chain-of-thought" reasoning.
- **Real-Time Streaming**: Watch the AI "think" and build your plan token-by-token via WebSockets.
- **Web Intelligence**: Enriches analysis with real-time market data from DuckDuckGo.
- **Privacy-First**: No data leaves your machine. Perfect for confidential business ideas.

## 🛠️ Tech Stack
- **Backend**: FastAPI, Python 3.10+, WebSockets.
- **Frontend**: Vanilla JS, Modern CSS (Glassmorphism, EB Garamond typography).
- **AI Engine**: Ollama running DeepSeek R1.

## 🏁 Getting Started

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai/) installed and running.
- Pull the DeepSeek R1 model:
  ```bash
  ollama pull deepseek-r1:1.5b
  ```

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Running the App
Run the start script:
```bash
start.bat
```
Or run manually via Uvicorn:
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser to: **http://localhost:8000**

## 📖 Viva / Defense
Check out [VIVA_GUIDE.md](./VIVA_GUIDE.md) for a comprehensive guide on the project's architecture and potential presentation questions.

---
Built with ❤️ for founders and product thinkers.
