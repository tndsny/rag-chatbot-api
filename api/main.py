from fastapi import FastAPI
from pydantic import BaseModel
from core.generator import answer

app = FastAPI(title="RAG Chatbot API")


class ChatRequest(BaseModel):
    query: str
    top_k: int = 3


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = answer(request.query, top_k=request.top_k)
    return result