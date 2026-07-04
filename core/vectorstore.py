import chromadb
from core.embedder import embed_texts

# Client persisten: data disimpan ke folder chroma_db/
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="documents")


def index_chunks(chunks: list[str], source: str):
    embeddings = embed_texts(chunks)
    ids = [f"{source}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": source} for _ in chunks]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=[e.tolist() for e in embeddings],
        metadatas=metadatas,
    )

def retrieve(query: str, top_k: int = 3):
    query_embedding = embed_texts([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
    )

    retrieved = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        retrieved.append({"text": doc, "source": meta["source"]})

    return retrieved