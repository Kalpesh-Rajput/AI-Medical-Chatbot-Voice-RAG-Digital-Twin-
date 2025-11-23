# backend/rag.py
import json
import hashlib
from typing import Tuple, List, Dict, Any
# from patches.fix_numpy2 import *

import chromadb
from sentence_transformers import SentenceTransformer

from backend.groq_client import groq_generate
from backend.cache_singleton import cache  # in-memory LRU cache singleton

# -------------------------------
#   Initialize embedder & Chroma
# -------------------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="medical_kb",
    metadata={"hnsw:space": "cosine"}
)

# -------------------------------
#   Retrieval
# -------------------------------

def retrieve_context(query: str, k: int = 3) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Return combined context string and the list of metadata dicts (sources).
    """
    query_emb = embedder.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=k
    )

    # results["documents"] is a list of lists (one per query), same for metadatas
    retrieved_docs = results.get("documents", [[]])[0] if results.get("documents") else []
    metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []

    combined_context = "\n\n".join(retrieved_docs) if retrieved_docs else ""

    return combined_context, metadatas


# -------------------------------
#   Prompt builder
# -------------------------------

def build_prompt(context: str, query: str, include_vitals: str = "") -> str:
    """
    Build a safe RAG prompt. Optionally include a small digital twin / vitals snapshot.
    """
    vitals_section = f"\n\nPatient Vitals: {include_vitals}" if include_vitals else ""
    prompt = f"""
You are a medical-domain AI assistant. Use ONLY the retrieved context to answer the user's question.
If the answer is not contained in the provided context, be honest and advise consulting a medical professional.

Retrieved Context:
--------------------
{context}
--------------------

{vitals_section}

User Question: {query}

Guidelines:
- Provide a clear, concise, and factual answer.
- Do NOT provide a medical diagnosis.
- If symptoms are severe or dangerous, instruct the user to seek immediate medical care.
- If applicable, cite the context or list the source URLs used.

Answer:
"""
    return prompt.strip()


# -------------------------------
#   Cache key helper
# -------------------------------

def make_cache_key(query: str, retrieved_sources: List[Dict[str, Any]]) -> str:
    """
    Create a stable hash key from the query and ordered list of retrieved source identifiers.
    retrieved_sources is expected to be a list of metadata dicts (e.g. [{'source': url}, ...])
    """
    sources_ids = [str(m.get("source") or m.get("id") or "") for m in retrieved_sources]
    key_obj = {"q": query.strip().lower(), "sources": sources_ids}
    raw = json.dumps(key_obj, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# -------------------------------
#   RAG orchestrator (no cache)
# -------------------------------

def answer_query(query: str, k: int = 3, include_vitals: str = "") -> Dict[str, Any]:
    """
    Basic RAG: retrieve -> build prompt -> LLM
    Returns dict: { "answer": str, "sources": list_of_metadatas }
    """
    context, sources = retrieve_context(query, k=k)
    prompt = build_prompt(context, query, include_vitals=include_vitals)
    answer = groq_generate(prompt)
    return {"answer": answer, "sources": sources}


# -------------------------------
#   RAG orchestrator with cache
# -------------------------------

def answer_query_with_cache(query: str, k: int = 3, ttl_seconds: int = 3600, include_vitals: str = "") -> Dict[str, Any]:
    """
    RAG pipeline with LRU TTL caching. Cache key = hash(query + retrieved_sources).
    Returns dict: { "answer": str, "sources": list_of_metadatas, "cached": bool }
    """
    # 1) Retrieve
    context, sources = retrieve_context(query, k=k)

    # 2) Build cache key
    cache_key = make_cache_key(query, sources)

    # 3) Check cache
    cached = cache.get(cache_key)
    if cached is not None:
        return {"answer": cached["answer"], "sources": sources, "cached": True}

    # 4) Build prompt and call LLM
    prompt = build_prompt(context, query, include_vitals=include_vitals)
    answer = groq_generate(prompt)

    # 5) Store in cache
    cache.set(cache_key, {"answer": answer, "prompt": prompt}, ttl=ttl_seconds)

    return {"answer": answer, "sources": sources, "cached": False}
