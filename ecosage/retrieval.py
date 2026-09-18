import json
import logging
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

import chromadb
from google import genai

from ecosage.config import get_settings
from ecosage.models import RetrievalResult, RetrievalTrace

logger = logging.getLogger(__name__)

# Thread-safe storage for retrieval traces
_trace_lock = threading.Lock()
_retrieval_traces: Dict[str, List[RetrievalTrace]] = {}

def log_trace(session_id: str, query: str, results: List[RetrievalResult], error: Optional[str] = None):
    """Log a retrieval trace for a session."""
    trace = RetrievalTrace(
        session_id=session_id,
        query=query,
        results=results,
        timestamp=datetime.now(timezone.utc).isoformat(),
        error=error
    )
    with _trace_lock:
        if session_id not in _retrieval_traces:
            _retrieval_traces[session_id] = []
        _retrieval_traces[session_id].append(trace)

def get_retrieval_trace(session_id: str) -> List[RetrievalTrace]:
    """
    Get all retrieval traces for a specific session.
    
    Args:
        session_id (str): The session ID.
        
    Returns:
        List[RetrievalTrace]: List of traces.
    """
    with _trace_lock:
        return _retrieval_traces.get(session_id, []).copy()

def get_query_embedding(query: str, client: genai.Client) -> List[float]:
    """Get embedding for the search query."""
    settings = get_settings()
    try:
        response = client.models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=query
        )
        if hasattr(response, 'embeddings'):
            return response.embeddings[0].values
        return response
    except Exception as e:
        logger.error(f"Error getting embedding for query: {e}")
        return []

def retrieve(query: str, top_k: int = 5, session_id: str = "default") -> List[RetrievalResult]:
    """
    Main vector search function.
    
    Args:
        query (str): The search query.
        top_k (int): Number of results to return.
        session_id (str): Session ID for trace logging.
        
    Returns:
        List[RetrievalResult]: List of retrieval results.
    """
    settings = get_settings()
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    
    try:
        chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        collection = chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )
    except Exception as e:
        logger.error(f"Error accessing ChromaDB: {e}")
        log_trace(session_id, query, [], error=str(e))
        return []
        
    query_embedding = get_query_embedding(query, client)
    if not query_embedding:
        log_trace(session_id, query, [], error="Failed to generate query embedding")
        return []
        
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
    except Exception as e:
        logger.error(f"Error querying ChromaDB: {e}")
        log_trace(session_id, query, [], error=str(e))
        return []
        
    retrieval_results = []
    
    if results and results.get("documents") and len(results["documents"]) > 0:
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]
        
        for doc, meta, distance in zip(docs, metas, distances):
            # Convert cosine distance to similarity score
            similarity = 1.0 - distance
            
            is_below_threshold = similarity < settings.SIMILARITY_THRESHOLD
            
            result = RetrievalResult(
                chunk_text=doc,
                source_id=meta.get("source_id", "UNKNOWN"),
                source_name=meta.get("source_name", "UNKNOWN"),
                similarity_score=similarity,
                metadata=meta,
                is_below_threshold=is_below_threshold
            )
            retrieval_results.append(result)
            
    log_trace(session_id, query, retrieval_results)
    return retrieval_results

def lookup_structured_table(table_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Direct lookup in JSON reference tables.
    
    Args:
        table_name (str): The JSON table name (without extension).
        filters (Dict[str, Any]): Dictionary of key-value pairs to filter by.
        
    Returns:
        List[Dict[str, Any]]: Filtered rows.
    """
    # Resolve path relative to the project
    base_dir = Path(__file__).resolve().parent.parent
    table_path = base_dir / "corpus" / "tables" / f"{table_name}.json"
    
    if not table_path.exists():
        logger.warning(f"Table not found: {table_path}")
        return []
        
    try:
        with open(table_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle nested JSON structure
        # The tables have keys like "benchmarks", "indices", "correlations"
        rows = data
        if isinstance(data, dict):
            # Find the list of records inside the dict
            for key in ["benchmarks", "indices", "correlations"]:
                if key in data:
                    rows = data[key]
                    break
            else:
                # If no known key, try the first list value
                for v in data.values():
                    if isinstance(v, list):
                        rows = v
                        break
        
        if not isinstance(rows, list):
            return []
            
        results = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            match = True
            for k, v in filters.items():
                if not v:  # skip empty filter values
                    continue
                row_val = str(row.get(k, "")).lower()
                filter_val = str(v).lower()
                if filter_val not in row_val and row_val != filter_val:
                    match = False
                    break
            if match:
                results.append(row)
                
        return results
    except Exception as e:
        logger.error(f"Error reading table {table_path}: {e}")
        return []
