from fastapi import FastAPI
from pydantic import BaseModel
from core.generator import answer

import os
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from core.generator import answer
from core.pdf_loader import extract_text_from_pdf
from core.chunker import chunk_text
from core.vectorstore import index_chunks

from core.vectorstore import index_chunks, reset_collection
from fastapi import FastAPI, File, UploadFile, HTTPException



app = FastAPI(title="RAG Chatbot API")


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]



@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = answer(request.question)
    return result

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Hanya file PDF yang diterima. File anda bertipe: {file.content_type}",
        )
    # 1. simpan PDF yang diupload ke folder data/
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 2. ekstrak -> reset -> chunk -> index
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    reset_collection()          # <- kosongkan collection lama supaya fokus ke dokumen yg baru diupload
    index_chunks(chunks, source=file.filename)

    # 3. Kembalikan info ke user
    return {
        "filename": file.filename,
        "total_chunks": len(chunks),
        "message": "PDF berhasil diindex, siap ditanya via /chat",
    }

@app.get("/")
def health():
    return {"status": "ok"}