from sentence_transformers import SentenceTransformer

# Model diload sekali saja, di level modul
model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: list[str]):
    embeddings = model.encode(texts)
    return embeddings