import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import chromadb
import uuid
import re

# -------- STEP 1: Define Medical Article Sources --------

URLS = [
    "https://www.medicalnewstoday.com/articles/150999",   # Fever
    "https://www.medicalnewstoday.com/articles/323627",   # Diabetes
    "https://www.medicalnewstoday.com/articles/73936",    # Headache
    "https://www.medicalnewstoday.com/articles/318716",   # High blood pressure
    "https://www.medicalnewstoday.com/articles/166606"    # Common cold
]


# -------- STEP 2: Clean text function --------

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\n", " ")
    return text.strip()


# -------- STEP 3: Scrape Article Paragraphs --------

def scrape_article(url):
    print(f"Scraping: {url}")
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")

        combined = " ".join([p.get_text() for p in paragraphs])
        return clean_text(combined)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""


# -------- STEP 4: Chunking Function --------

def chunk_text(text, chunk_size=800, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


# -------- STEP 5: Embeddings + ChromaDB --------

def ingest_documents():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(
        name="medical_kb",
        metadata={"hnsw:space": "cosine"}
    )

    for url in URLS:
        text = scrape_article(url)
        if len(text) < 500:
            print(f"Skipping {url} (content too short)")
            continue

        chunks = chunk_text(text)

        for chunk in chunks:
            embedding = model.encode(chunk).tolist()
            uid = str(uuid.uuid4())

            collection.add(
                ids=[uid],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"source": url}]
            )

    print("\nIngestion Complete! ChromaDB is ready.")


if __name__ == "__main__":
    ingest_documents()
