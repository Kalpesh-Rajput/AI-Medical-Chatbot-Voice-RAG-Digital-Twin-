import os

folders = [
    "backend",
    "scripts",
    "data",
    "scraped_data",
    "chroma_db",
    "tests",
    "docs"
]

files = {
    "app.py": "",
    "README.md": "",
    "backend/__init__.py": "",
    "backend/embeddings.py": "",
    "backend/retriever.py": "",
    "backend/ollama_client.py": "",
    "backend/rag.py": "",
    "backend/db.py": "",
    "backend/cache.py": "",
    "backend/digital_twin.py": "",
    "scripts/ingest.py": ""
}

print("Creating folders...")
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Created folder: {folder}")

print("\nCreating files...")
for filepath, content in files.items():
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created file: {filepath}")

print("\nProject structure created successfully!")
