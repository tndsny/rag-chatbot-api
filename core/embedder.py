from sentence_transformers import SentenceTransformer

# notes : di upload sekali saja di level module
model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: list[str]):
    embeddings = model.encode(texts)
    return embeddings