import re
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from google import genai
from ecosage.config import get_settings

def chunk_markdown(text: str, source_id: str, source_name: str) -> List[Dict[str, Any]]:
    """
    Split markdown by ## and ### headings into chunks with metadata.
    
    Args:
        text (str): The raw markdown text.
        source_id (str): The source ID.
        source_name (str): The source name.
        
    Returns:
        List[Dict[str, Any]]: List of dictionary chunks.
    """
    chunks = []
    pattern = re.compile(r'^(#{2,3})\s+(.*)', re.MULTILINE)
    matches = list(pattern.finditer(text))
    
    if not matches:
        return [{"text": text.strip(), "source_id": source_id, "source_name": source_name, "section": "Root", "chunk_index": 0}]
    
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i+1].start() if i + 1 < len(matches) else len(text)
        chunk_text = text[start:end].strip()
        section = match.group(2).strip()
        
        chunks.append({
            "text": chunk_text,
            "source_id": source_id,
            "source_name": source_name,
            "section": section,
            "chunk_index": i
        })
        
    return chunks

def extract_source_id(text: str) -> str:
    """
    Extract source ID from document text (pattern: 'Source ID: XXX').
    
    Args:
        text (str): The document text.
        
    Returns:
        str: The extracted source ID or 'UNKNOWN'.
    """
    match = re.search(r'Source ID:\s*(\S+)', text)
    return match.group(1) if match else "UNKNOWN"

def get_embeddings(texts: List[str], client: genai.Client) -> List[List[float]]:
    """
    Get embeddings from Gemini API, with batching for rate limits.
    
    Args:
        texts (List[str]): List of texts to embed.
        client (genai.Client): GenAI client.
        
    Returns:
        List[List[float]]: List of embeddings.
    """
    settings = get_settings()
    batch_size = 5
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            response = client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=batch
            )
            # Depending on SDK version, we check how it returns
            if hasattr(response, 'embeddings'):
                batch_embeddings = [emb.values for emb in response.embeddings]
            else:
                batch_embeddings = response
            embeddings.extend(batch_embeddings)
            time.sleep(1.0)
        except Exception as e:
            print(f"Error generating embeddings for batch {i}: {e}")
            embeddings.extend([[] for _ in batch])
            
    return embeddings

def load_structured_tables(tables_dir: Path) -> List[Dict[str, Any]]:
    """
    Load JSON reference tables and convert to searchable text chunks.
    
    Args:
        tables_dir (Path): Directory containing JSON tables.
        
    Returns:
        List[Dict[str, Any]]: List of dictionary chunks.
    """
    chunks = []
    if not tables_dir.exists():
        return chunks
        
    for json_file in tables_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle nested structure: extract the list of records
            rows = data
            source_id = "UNKNOWN"
            if isinstance(data, dict):
                source_id = data.get("source", f"table_{json_file.stem}")
                for key in ["benchmarks", "indices", "correlations"]:
                    if key in data:
                        rows = data[key]
                        break
                else:
                    for v in data.values():
                        if isinstance(v, list):
                            rows = v
                            break
            
            if isinstance(rows, list):
                for i, row in enumerate(rows):
                    if isinstance(row, dict):
                        text_rep = ", ".join(f"{k}: {v}" for k, v in row.items())
                        chunks.append({
                            "text": text_rep,
                            "source_id": source_id,
                            "source_name": json_file.name,
                            "section": f"row_{i}",
                            "chunk_index": i,
                            "type": "structured_table"
                        })
        except Exception as e:
            print(f"Error loading table {json_file}: {e}")
            
    return chunks

def ingest(force: bool = False):
    """
    Main ingestion pipeline.
    
    Args:
        force (bool): Force re-ingestion if True.
    """
    settings = get_settings()
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    
    Path(settings.CHROMA_PATH).mkdir(parents=True, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
    
    if force:
        try:
            chroma_client.delete_collection(name=settings.CHROMA_COLLECTION)
        except Exception:
            pass
            
    collection = chroma_client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )
    
    if collection.count() > 0 and not force:
        print(f"Collection already has {collection.count()} documents. Use --force to re-ingest.")
        return
        
    base_dir = Path(__file__).resolve().parent.parent
    corpus_dir = base_dir / "corpus" / "raw"
    tables_dir = base_dir / "corpus" / "tables"
    
    all_chunks = []
    
    if corpus_dir.exists():
        for md_file in corpus_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                source_id = extract_source_id(content)
                chunks = chunk_markdown(content, source_id, md_file.name)
                all_chunks.extend(chunks)
                print(f"Processed {md_file.name}: {len(chunks)} chunks.")
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
                
    table_chunks = load_structured_tables(tables_dir)
    all_chunks.extend(table_chunks)
    
    if not all_chunks:
        print("No documents to ingest.")
        return
        
    print(f"Total chunks to embed: {len(all_chunks)}")
    
    texts = [c["text"] for c in all_chunks]
    embeddings = get_embeddings(texts, client)
    
    ids = []
    metadatas = []
    documents = []
    valid_embeddings = []
    
    for idx, (chunk, emb) in enumerate(zip(all_chunks, embeddings)):
        if not emb:
            continue
        chunk_type = chunk.get("type", "doc")
        ids.append(f"{chunk['source_id']}_{chunk_type}_{idx}")
        documents.append(chunk["text"])
        valid_embeddings.append(emb)
        
        meta = {
            "source_id": chunk["source_id"],
            "source_name": chunk["source_name"],
            "section": chunk["section"],
            "chunk_index": chunk["chunk_index"],
        }
        if "type" in chunk:
            meta["type"] = chunk["type"]
        metadatas.append(meta)
        
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i+batch_size],
            embeddings=valid_embeddings[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            documents=documents[i:i+batch_size]
        )
        print(f"Inserted batch {i//batch_size + 1}")
        
    print(f"Ingestion complete. Added {len(ids)} documents.")

if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    ingest(force=force_flag)
