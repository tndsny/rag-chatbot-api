from core.loader import load_documents
from core.chunker import chunk_text
from core.vectorstore import index_chunks, retrieve

# 1. Index semua dokumen
docs = load_documents()
for doc in docs:
    chunks = chunk_text(doc["text"])
    index_chunks(chunks, source=doc["source"])
    print(f"Indexed {len(chunks)} chunk dari {doc['source']}")

# 2. Tanya sesuatu
query = "Apa itu sistem rudal Bavar-373?"
print(f"\nPertanyaan: {query}\n")

results = retrieve(query, top_k=3)

# 3. Lihat hasil retrieval
for i, r in enumerate(results, 1):
    print(f"--- Hasil {i} (sumber: {r['source']}) ---")
    print(r["text"][:200], "...\n")