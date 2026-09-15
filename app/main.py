from fastapi import FastAPI, Depends

from app.services.auth_service import authenticate
from app.services.rbac_service import get_allowed_departments

from app.services.vector_store import VectorStore

from app.services.rag_service import RAGService

app = FastAPI(
    title="FinSolve Internal AI Assistant",
    description="Role-Based RAG Chatbot",
    version="0.1.0",
)

vector_store = VectorStore()

rag_service = RAGService()

@app.get("/login")
def login(user=Depends(authenticate)):
    return {
        "message": f"Welcome {user['username']}!",
        "role": user["role"],
        "allowed_departments": get_allowed_departments(user["role"]),
    }


@app.get("/test")
def test(user=Depends(authenticate)):
    return {
        "message": f"Hello {user['username']}! You can now chat.",
        "role": user["role"],
    }


@app.post("/chat")
def chat(
    message: str = "Hello",
    user=Depends(authenticate),
):
    result = rag_service.answer(
        query=message,
        role=user["role"],
    )

    return {
        "user": user["username"],
        "role": user["role"],
        "message": message,
        "answer": result["answer"],
        "sources": result["sources"],
    }