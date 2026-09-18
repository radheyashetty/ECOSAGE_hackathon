"""FastAPI application for EcoSage."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ecosage.models import EcoSageInput, EcoSageResponse, RetrievalTrace
from ecosage.orchestrator import process_input
from ecosage.retrieval import get_retrieval_trace
from ecosage.ingest import ingest

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure knowledge base is ingested
    try:
        ingest(force=False)  # Only ingests if collection is empty
    except Exception as e:
        print(f"Warning: Failed to ingest on startup: {e}")
    yield

app = FastAPI(
    title="EcoSage API",
    description="AI Environmental Scientist for Biodiversity Intelligence",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=EcoSageResponse)
async def chat(input_data: EcoSageInput):
    """Main conversation endpoint."""
    try:
        return process_input(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/retrieval/{session_id}")
async def debug_retrieval(session_id: str):
    """Retrieval trace inspection endpoint (FR-1.4)."""
    try:
        traces = get_retrieval_trace(session_id)
        return {"session_id": session_id, "traces": [t.model_dump() for t in traces]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ecosage"}

@app.post("/ingest")
async def trigger_ingest(force: bool = False):
    """Trigger corpus re-ingestion."""
    try:
        ingest(force=force)
        return {"status": "ingestion complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
