from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import agent

app = FastAPI(
    title="Anna — Acme Financial Secure AI Assistant",
    description="Hardened internal AI assistant. REST API only.",
    docs_url=None,   # Swagger UI disabled
    redoc_url=None
)


class ChatRequest(BaseModel):
    message: str
    session_id: str


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

@app.post("/chat")
async def chat(request: ChatRequest):
    result = agent.chat(request.message, request.session_id)
    return JSONResponse(result)


# ---------------------------------------------------------------------------
# Session management — requires X-Session-ID header
# ---------------------------------------------------------------------------

@app.get("/history")
async def get_history(x_session_id: Optional[str] = Header(default=None)):
    if not x_session_id:
        raise HTTPException(status_code=401, detail="X-Session-ID header required.")
    return JSONResponse({"history": agent.get_session_history(x_session_id)})


@app.post("/reset")
async def reset(x_session_id: Optional[str] = Header(default=None)):
    if not x_session_id:
        raise HTTPException(status_code=401, detail="X-Session-ID header required.")
    agent.reset_session(x_session_id)
    return JSONResponse({"status": "Session cleared."})


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "agent": "Anna"}
