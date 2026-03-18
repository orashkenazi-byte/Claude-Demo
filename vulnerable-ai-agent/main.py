from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import traceback
import agent
from datastore import CUSTOMERS, INTERNAL_DOCUMENTS

app = FastAPI(
    title="Acme Financial AI Assistant",
    description="Internal AI assistant — Acme Financial Services"
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# Main routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("static/index.html") as f:
        return f.read()


@app.post("/chat")
async def chat(request: ChatRequest):
    # VULNERABILITY: No input sanitization, no rate limiting.
    # Full stack traces returned on error (no error sanitization).
    try:
        result = agent.chat(request.message)
        return JSONResponse(result)
    except Exception:
        # VULNERABILITY: Raw stack trace returned to client
        return JSONResponse({"error": traceback.format_exc()}, status_code=500)


# ---------------------------------------------------------------------------
# Unauthenticated data endpoints (intentional vulnerabilities)
# ---------------------------------------------------------------------------

@app.get("/history")
async def get_history():
    # VULNERABILITY: No auth, no session isolation — returns all users' conversation history
    return JSONResponse({"history": agent.get_history()})


@app.post("/reset")
async def reset():
    agent.reset_history()
    return JSONResponse({"status": "History cleared"})


# ---------------------------------------------------------------------------
# Debug endpoints (intentional info disclosure)
# ---------------------------------------------------------------------------

@app.get("/debug/system-prompt")
async def debug_system_prompt():
    # VULNERABILITY: System prompt exposed with no authentication
    return JSONResponse({"system_prompt": agent.SYSTEM_PROMPT})


@app.get("/debug/datastore")
async def debug_datastore():
    # VULNERABILITY: Entire data store exposed with no authentication
    return JSONResponse({
        "customers": CUSTOMERS,
        "documents": INTERNAL_DOCUMENTS
    })
