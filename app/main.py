from __future__ import annotations
import os
import re
import uuid
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agent.agent import agent
from app.agent.memory import SessionMemory
from app.agent.router import detect_intent
from app.agent import tools as tools_module

from dotenv import load_dotenv


load_dotenv()

# In-memory sessions (swap with Redis/Postgres in production)
SESSIONS: Dict[str, SessionMemory] = {}

def ensure_session(session_id: Optional[str]) -> str:
    sid = session_id or str(uuid.uuid4())
    if sid not in SESSIONS:
        SESSIONS[sid] = SessionMemory()
    return sid

# Inject global SESSIONS into tools module so @tool functions can access it
tools_module.SESSIONS = SESSIONS

app = FastAPI(title="Conversational Data Explorer (Agno + Gemini + Plotly)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static plots
STATIC_PLOTS_DIR = os.path.join(os.path.dirname(__file__), "static", "plots")
app.mount("/plots", StaticFiles(directory=STATIC_PLOTS_DIR), name="plots")

class ChatIn(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatOut(BaseModel):
    session_id: str
    reply: str
    tables: Optional[List[Dict[str, Any]]] = None
    chart_data: Optional[Dict[str, Any]] = None
    clarifying_question: Optional[str] = None
    error: Optional[str] = None

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/upload")
async def upload(file: UploadFile = File(...), session_id: Optional[str] = Form(None), name: Optional[str] = Form("dataset")):
    sid = ensure_session(session_id)
    data = await file.read()
    
    # Call the function directly without going through the @tool decorator
    from app.agent.tools import get_or_create_session
    import io
    import pandas as pd
    from app.services.utils import snake_case, infer_schema
    
    mem = get_or_create_session(sid)

    # Try CSV
    try:
        buf = io.BytesIO(data)
        buf.seek(0)
        df = pd.read_csv(buf)
    except Exception:
        # Fallback to Excel
        buf = io.BytesIO(data)
        buf.seek(0)
        df = pd.read_excel(buf, sheet_name=0)

    # Normalize headers
    df.columns = [snake_case(c) for c in df.columns]

    # Opportunistic typing: dates & numerics (safe, non-destructive)
    for c in df.columns:
        # date-like
        if any(tok in c for tok in ["date", "time", "timestamp"]):
            try:
                df[c] = pd.to_datetime(df[c], errors="ignore")
            except Exception:
                pass
        # numeric coercion for string/object columns
        if df[c].dtype == object:
            try:
                coerced = pd.to_numeric(df[c], errors="coerce")
                if coerced.notna().sum() > max(10, int(0.5 * len(df))):
                    df[c] = coerced
            except Exception:
                pass

    mem.registry.put(name, df)
    schema = infer_schema(df)
    res = {"session_id": sid, "name": name, "rows": len(df), "cols": list(df.columns), "schema": schema}
    
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.post("/chat", response_model=ChatOut)
async def chat(body: ChatIn):
    sid = ensure_session(body.session_id)
    print(f"Chat session ID: {sid}")
    print(f"Available sessions: {list(SESSIONS.keys())}")
    
    # Check if session has data
    if sid in SESSIONS:
        print(f"Session {sid} registry tables: {list(SESSIONS[sid].registry.tables.keys())}")
        print(f"Session {sid} active: {SESSIONS[sid].registry.active}")

    # Example clarification: user asks for a "trend"/"plot" without a known date column
    intent = detect_intent(body.message)
    mem = SESSIONS[sid]
    if intent == "PLOT":
        # If they reference "trend" but no obvious datetime column is saved, we can suggest options
        try:
            df = mem.registry.get()
            dt_candidates = [c for c in df.columns if any(tok in c.lower() for tok in ["date", "time", "timestamp"])]
            if not dt_candidates:
                # Ask clarifying question
                q = "Which column should be used on the x-axis? (Provide any column name)"
                return ChatOut(session_id=sid, reply=q, clarifying_question=q)
        except Exception:
            pass

    # Delegate to agent (it will choose tools using function-calling)
    # Add session context to the message
    message_with_context = f"[SESSION_ID: {sid}] {body.message}"
    agent_result = agent.run(message_with_context)
    reply = agent_result.content

    # Simple heuristic: remember date column if user says "use <something_date>"
    low = body.message.lower()
    if "use " in low and "date" in low:
        for token in re.split(r"[^a-z0-9_]+", low):
            if "date" in token:
                mem.remember("date_col", token)

    # Check if the agent used tool_plot and retrieve chart data from session memory
    chart_data = mem.recall("last_chart")
    if chart_data:
        mem.remember("last_chart", None)  # Clear it after use
    
    # Extract any tables from agent response (for tool_top_k, tool_describe, etc.)
    tables = None
    # This is a simple approach - you might want to enhance this based on your needs

    return ChatOut(session_id=sid, reply=reply, chart_data=chart_data, tables=tables)

class ResetIn(BaseModel):
    session_id: Optional[str] = None

@app.post("/reset")
async def reset(body: ResetIn):
    sid = ensure_session(body.session_id)
    SESSIONS[sid] = SessionMemory()
    return {"session_id": sid, "status": "reset"}