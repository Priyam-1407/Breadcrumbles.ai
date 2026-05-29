from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI(title="breadcrumbles.ai", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"  # change to whatever model you have pulled e.g. "mistral", "codellama"


# ── Request / Response schemas ──────────────────────────────────────────────

class ProblemRequest(BaseModel):
    problem: str          # the DSA / coding problem description
    language: str = "Python"   # optional: target language


class HintResponse(BaseModel):
    hint: str
    level: int            # 1 = slight, 2 = approach, 3 = pseudocode


# ── Helper: call Ollama ──────────────────────────────────────────────────────

async def ask_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail="Cannot reach Ollama. Make sure it is running: `ollama serve`"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# ── ENDPOINT 1  /hint/1  — The Slight Hint ──────────────────────────────────

@app.post("/hint/1", response_model=HintResponse)
async def slight_hint(req: ProblemRequest):
    """
    Level 1 – nudge the user in the right direction without revealing anything.
    Think of it as a gentle 'think about X' prompt.
    """
    prompt = f"""You are a DSA tutor. A student is stuck on this problem:

\"\"\"{req.problem}\"\"\"

Give them ONE very slight hint. Do NOT reveal the algorithm or data structure.
Only nudge them to think about the right angle. 
Keep it to 2-3 short sentences. No code. No spoilers.
Language context: {req.language}"""

    hint_text = await ask_ollama(prompt)
    return HintResponse(hint=hint_text, level=1)


# ── ENDPOINT 2  /hint/2  — The Approach Hint ────────────────────────────────

@app.post("/hint/2", response_model=HintResponse)
async def approach_hint(req: ProblemRequest):
    """
    Level 2 – reveal the high-level approach / strategy without writing code.
    """
    prompt = f"""You are a DSA tutor. A student is stuck on this problem:

\"\"\"{req.problem}\"\"\"

Give them an APPROACH hint. Name the algorithm or data structure family 
(e.g. sliding window, two pointers, BFS, DP, stack, etc.) and briefly explain 
WHY it fits this problem. Still no code. 4-6 sentences max.
Language context: {req.language}"""

    hint_text = await ask_ollama(prompt)
    return HintResponse(hint=hint_text, level=2)


# ── ENDPOINT 3  /hint/3  — The Pseudocode Hint ──────────────────────────────

@app.post("/hint/3", response_model=HintResponse)
async def pseudocode_hint(req: ProblemRequest):
    """
    Level 3 – provide clean pseudocode so the student can implement themselves.
    """
    prompt = f"""You are a DSA tutor. A student is stuck on this problem:

\"\"\"{req.problem}\"\"\"

Give them a PSEUDOCODE hint in {req.language} style. 
Write clean pseudocode (not runnable code) that outlines:
1. The main idea / approach
2. Key steps with brief comments
3. Time and space complexity at the end

Do NOT write actual runnable code. Use plain English steps + indentation."""

    hint_text = await ask_ollama(prompt)
    return HintResponse(hint=hint_text, level=3)


# ── Health check ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "breadcrumbles.ai is running 🍞", "endpoints": ["/hint/1", "/hint/2", "/hint/3"]}


@app.get("/health")
async def health():
    # ping ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get("http://localhost:11434/api/tags")
            models = [m["name"] for m in r.json().get("models", [])]
            return {"status": "ok", "ollama": "reachable", "available_models": models}
    except Exception:
        return {"status": "degraded", "ollama": "unreachable — run `ollama serve`"}
