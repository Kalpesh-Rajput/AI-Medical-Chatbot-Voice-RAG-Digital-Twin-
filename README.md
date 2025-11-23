# Medical Chatbot — Project Documentation

**Based on assignment PDF:** `/mnt/data/Fresher — Technical Problem Statements 2 - Takeaway test_AI-ML.pdf`

---

## 1. Project Summary

**Objective:** Build an MVP medical-domain chatbot using Retrieval-Augmented Generation (RAG) that integrates:
- a small knowledge base scraped from public medical articles,
- a vector store (ChromaDB) with embeddings from `sentence-transformers`,
- an LLM backend (Groq API in this implementation),
- a Streamlit UI with both text and voice input,
- a simple Digital Twin (patient vitals simulator),
- caching for fast repeated queries.

**Scope:** Educational/demo. Not for medical diagnosis.

---

## 2. Tech Stack

- **Frontend / UI:** Streamlit
- **LLM API:** Groq (free tier)
- **Vector DB / RAG:** ChromaDB
- **Embeddings:** `sentence-transformers` (all-MiniLM-L6-v2)
- **Scraping:** requests + BeautifulSoup4
- **Voice:** PyAudio + SpeechRecognition (local recording flow used for Windows). Alternative browser-based options noted.
- **Cache:** In-memory LRU with TTL
- **Database (optional):** SQLite for logs (skipped per preference)
- **Language:** Python 3.10

---

## 3. High-Level Design (HLD)

**Components:**
1. **Streamlit App (`app.py`)**
   - UI for chat, voice recording, digital twin display, and source listing.
2. **Ingestion Script (`scripts/ingest.py`)**
   - Scrapes medical articles, cleans text, chunks long text, computes embeddings, and stores vectors to ChromaDB.
3. **RAG Orchestrator (`backend/rag.py`)**
   - Retrieves top-k chunks from Chroma, builds a prompt, calls Groq LLM, and returns answer and sources.
4. **LLM Client (`backend/groq_client.py`)**
   - Wraps Groq API calls and handles responses.
5. **Digital Twin (`backend/digital_twin.py`)**
   - Simulates patient vitals and provides JSON snapshots.
6. **Cache (`backend/cache.py`, `backend/cache_singleton.py`)**
   - LRU cache with TTL to avoid redundant LLM calls.
7. **(Optional) Logger (`backend/logger.py`)**
   - SQLite-based conversation logs — optional and skipped by user.

**High-level flow:**
User (text/voice) → Streamlit UI → RAG (embed-query → Chroma retrieve) → Groq LLM → Answer → UI + cache + (optional log)

---

## 4. Low-Level Design (LLD)

**File-level description**

- `app.py`
  - Imports RAG orchestrator, Digital Twin, cache indicator.
  - Handles user input, voice recording, triggers `answer_query_with_cache`.
  - Shows vitals, chat history, and sources.

- `scripts/ingest.py`
  - `scrape_article(url)`: fetches and extracts paragraphs.
  - `clean_text(text)`: whitespace and newline normalization.
  - `chunk_text(text, chunk_size=800, overlap=200)`.
  - Stores vectorized chunks to ChromaDB with metadata `{"source": url}`.

- `backend/embeddings.py`
  - Wrapper functions to return embeddings using SentenceTransformers.

- `backend/rag.py`
  - `retrieve_context(query, k)`: returns combined context and sources.
  - `build_prompt(context, query, include_vitals)`: returns a safety-guided prompt.
  - `answer_query_with_cache(...)`: checks cache, calls `groq_generate`, stores result.

- `backend/groq_client.py`
  - `groq_generate(prompt, max_tokens, temperature)`: calls Groq Python SDK and returns response content.

- `backend/digital_twin.py`
  - `PatientDigitalTwin` class: `get_vitals()`, `update_vitals()`, `get_vitals_json()`.

- `backend/cache.py` and `backend/cache_singleton.py`
  - LRU cache with TTL; singleton instance for app use.

---

## 5. Data Flow Diagram (textual)

1. **User** enters question (text or voice) in Streamlit.
2. If voice: record audio → SpeechRecognition → text.
3. Streamlit sends query to **RAG**:
   - Embed query with `all-MiniLM-L6-v2`.
   - Query ChromaDB for top-k similar chunks.
   - Combine chunks into context.
   - Build safety-aware prompt (include vitals optionally).
4. Send prompt to **Groq LLM** → receive answer.
5. Answer displayed to user with sources; cached for repeated queries.

---

## 6. Prompt Template (example)

```
You are a medical-domain AI assistant.
Use ONLY the following retrieved context to answer the user's question.
If the answer is not in the context, advise consulting a medical professional.

Retrieved Context:
--------------------
{context}
--------------------

Patient Vitals: {vitals}

User Question: {query}

Guidelines:
- Provide a clear, concise, factual answer.
- Do NOT provide a medical diagnosis.
- If symptoms are severe, instruct immediate medical care.
- Cite the context or list the source URLs used.

Answer:
```


---

## 7. Security & Ethics

- **Disclaimer** visible in UI: not for medical diagnosis.
- **Data privacy:** Do not log PII; user voice data transient.
- **Source citation:** every answer shows retrieved sources.

---

## 8. Future Improvements

- Add user authentication & role-based access.
- Replace PyAudio flow with browser-based WebRTC for cross-platform voice.
- Add better chunking and semantic reranking.
- Fine-tune an open-source model on medical QA for better precision.
- Add unit tests, CI/CD, and containerization.

---

## 09. Appendix & Files
- Project files: `app.py`, `backend/`, `scripts/ingest.py`, `requirements.txt`
- Assignment PDF used: `/mnt/data/Fresher — Technical Problem Statements 2 - Takeaway test_AI-ML.pdf`

---

*End of documentation.*
