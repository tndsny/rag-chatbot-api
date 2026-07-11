import os
from dotenv import load_dotenv
from groq import Groq
from core.vectorstore import retrieve

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_context(chunks: list[dict]):
    parts = []
    for c in chunks:
        parts.append(f"[Sumber: {c['source']}]\n{c['text']}")
    return "\n\n".join(parts)


def answer(query: str, top_k: int = 3):
    chunks = retrieve(query, top_k=top_k)
    context = build_context(chunks)

    prompt = f"""Kamu asisten yang menjawab pertanyaan HANYA berdasarkan konteks di bawah.

Aturan:
- Jika jawaban ADA di konteks: jawab dengan jelas, lalu sebutkan sumber (nama file) yang kamu pakai.
- Jika jawaban TIDAK ADA di konteks: jawab HANYA dengan kalimat "Maaf, informasi itu tidak ada di dokumen." TANPA menyebut sumber, nama file, atau apa pun setelahnya.

Konteks:
{context}

Pertanyaan: {query}

Jawaban:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": list({c["source"] for c in chunks}),
    }