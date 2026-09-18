"""FastAPI application for EcoSage with structured error handling and logging."""
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ecosage.causal_graph import get_graph_summary
from ecosage.config import get_settings
from ecosage.exceptions import EcoSageError
from ecosage.ingest import ingest
from ecosage.logger import setup_logger
from ecosage.models import EcoSageInput, EcoSageResponse
from ecosage.orchestrator import process_input
from ecosage.retrieval import get_retrieval_trace

logger = setup_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: log startup, verify collection, and handle graceful shutdown."""
    logger.info("🌿 Initializing EcoSage API Server...")
    settings = get_settings()
    logger.info(f"Active LLM Provider: {settings.LLM_PROVIDER} | Model: {settings.LLM_MODEL}")
    try:
        ingest(force=False)
        logger.info("Knowledge base index verified.")
    except Exception as e:
        logger.warning(f"Non-fatal knowledge base check on startup: {e}")
    yield
    logger.info("EcoSage API Server shutting down.")


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


@app.exception_handler(EcoSageError)
async def ecosage_error_handler(request: Request, exc: EcoSageError) -> JSONResponse:
    """Handle custom EcoSage domain exceptions."""
    logger.error(f"Domain error on {request.url.path}: {exc.message} | Details: {exc.details}")
    return JSONResponse(
        status_code=400,
        content={
            "error_type": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
            "path": str(request.url.path),
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all failsafe exception handler."""
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error_type": "InternalServerError",
            "message": "An unexpected error occurred. The system failsafe has logged this incident.",
            "path": str(request.url.path),
        }
    )


@app.post("/chat", response_model=EcoSageResponse)
async def chat(input_data: EcoSageInput) -> EcoSageResponse:
    """Main conversation endpoint."""
    logger.info(f"Incoming /chat request | session_id: {input_data.session_id}")
    try:
        response = process_input(input_data)
        logger.info(
            f"Completed /chat | session_id: {response.session_id} | "
            f"recs: {len(response.recommendations)} | questions: {len(response.clarifying_questions)}"
        )
        return response
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/debug/retrieval/{session_id}")
async def debug_retrieval(session_id: str) -> dict[str, Any]:
    """Retrieval trace inspection endpoint (FR-1.4)."""
    try:
        traces = get_retrieval_trace(session_id)
        return {
            "session_id": session_id,
            "trace_count": len(traces),
            "traces": [t.model_dump() for t in traces],
        }
    except Exception as e:
        logger.error(f"Error retrieving debug trace: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "ecosage", "version": "1.0.0"}


@app.get("/system/status")
async def system_status() -> dict[str, Any]:
    """System health and diagnostic inspection endpoint."""
    settings = get_settings()
    graph_stats = get_graph_summary()
    return {
        "status": "operational",
        "provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
        "causal_graph": graph_stats,
        "logging": "enabled",
        "failsafe_mode": "ready",
    }


@app.post("/ingest")
async def trigger_ingest(force: bool = False) -> dict[str, str]:
    """Trigger corpus re-ingestion."""
    try:
        logger.info(f"Triggering corpus ingestion (force={force})...")
        ingest(force=force)
        return {"status": "ingestion complete"}
    except Exception as e:
        logger.error(f"Error during triggered ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
