# 🍞 breadcrumbles.ai

> A DSA / coding hint engine with 3 progressive hint levels.  
> Built with **FastAPI** + **Ollama** (local LLM).

---

## What this project does

You give it a coding problem. It gives you hints — but only as much as you ask for:

| Endpoint   | Hint Level       | What you get                                      |
|------------|------------------|---------------------------------------------------|
| `POST /hint/1` | Slight hint  | A gentle nudge — think about *this angle*         |
| `POST /hint/2` | Approach hint | The algorithm/data-structure name + why it fits  |
| `POST /hint/3` | Pseudocode hint | Step-by-step pseudocode, no runnable code yet   |

---

## Project Structure

```
breadcrumbles/
├── backend/
│   ├── main.py          ← FastAPI app (all 3 endpoints)
│   └── requirements.txt
└── frontend/
    └── index.html       ← standalone UI (open in browser)
```

---

## Prerequisites

1. **Python 3.10+** installed
2. **Ollama** installed → https://ollama.com/download
3. A model pulled in Ollama (see step 2 below)

---

## Setup — Step by Step

### Step 1 — Install & start Ollama

```bash
# Download from https://ollama.com/download and install
# Then start the Ollama server:
ollama serve
```

### Step 2 — Pull a model

```bash
# Pick ONE of these (llama3.2 is recommended, ~2GB):
ollama pull llama3.2

# Alternatives:
ollama pull mistral        # good for code
ollama pull codellama      # specialised for code
ollama pull phi3           # lighter/faster
```

> After pulling, check your model name with `ollama list`  
> Then open `backend/main.py` and update line 10:  
> `MODEL = "llama3.2"  ← change this to match your pulled model`

### Step 3 — Install Python dependencies

```bash
cd breadcrumbles/backend
pip install -r requirements.txt
```

### Step 4 — Run the FastAPI server

```bash
# From inside the backend/ folder:
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### Step 5 — Open the frontend

Just open `frontend/index.html` in your browser. No build step needed.

```bash
# macOS
open frontend/index.html

# Linux
xdg-open frontend/index.html

# Windows
start frontend/index.html
```

---

## Testing the API directly (without the UI)

Visit the interactive docs at: **http://localhost:8000/docs**

Or use curl:

```bash
# Hint 1 — slight hint
curl -X POST http://localhost:8000/hint/1 \
  -H "Content-Type: application/json" \
  -d '{"problem": "Given an array, find two numbers that add up to a target. Return their indices.", "language": "Python"}'

# Hint 2 — approach hint
curl -X POST http://localhost:8000/hint/2 \
  -H "Content-Type: application/json" \
  -d '{"problem": "Given an array, find two numbers that add up to a target. Return their indices.", "language": "Python"}'

# Hint 3 — pseudocode
curl -X POST http://localhost:8000/hint/3 \
  -H "Content-Type: application/json" \
  -d '{"problem": "Given an array, find two numbers that add up to a target. Return their indices.", "language": "Python"}'

# Health check (also shows available Ollama models)
curl http://localhost:8000/health
```

---

## How the request/response connects (the backbone concept)

```
Browser (UI)
    │
    │  POST /hint/1
    │  Body: { "problem": "...", "language": "Python" }
    ▼
FastAPI (main.py)
    │
    │  Builds a prompt string
    │  POST http://localhost:11434/api/generate
    │  Body: { "model": "llama3.2", "prompt": "...", "stream": false }
    ▼
Ollama (local LLM)
    │
    │  Returns: { "response": "hint text here..." }
    ▼
FastAPI
    │
    │  Returns: { "hint": "...", "level": 1 }
    ▼
Browser (displays the hint)
```

This pattern — **client → API → external service → API → client** — is the backbone of almost every real-world app you'll ever build.

---

## Changing the model

Open `backend/main.py`, line 10:

```python
MODEL = "llama3.2"   # ← change this
```

Available models (after `ollama pull`):
- `llama3.2` — general, great quality
- `mistral` — fast, good at code
- `codellama` — fine-tuned on code
- `phi3` — lightweight, runs on CPU easily

---

## Common Issues

| Problem | Fix |
|---------|-----|
| `503 Cannot reach Ollama` | Run `ollama serve` in a separate terminal |
| `404 model not found` | Run `ollama pull llama3.2` then check `MODEL` in main.py |
| CORS error in browser | Already handled — `allow_origins=["*"]` is set |
| Slow responses | Normal for first call (model loads into memory). Subsequent calls are faster. |
| Port 8000 in use | Run with `--port 8001` and update the API URL in the frontend |
