from app.services.vector_store import VectorStore
from app.services.rbac_service import get_allowed_departments

from app.services.llm_service import LLMService

class RAGService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm_service = LLMService()

    def answer(self, query: str, role: str):
        allowed_departments = get_allowed_departments(role)

        results = self.vector_store.search(
    query=query,
    allowed_departments=allowed_departments,
    n_results=5,
)

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        MAX_CONTEXT_CHUNKS = 3

        retrieved = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            retrieved.append(
                {
                    "document": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        retrieved.sort(key=lambda item: item["distance"])

        retrieved = retrieved[:MAX_CONTEXT_CHUNKS]

        documents = [
            item["document"]
            for item in retrieved
        ]

        metadatas = [
            item["metadata"]
            for item in retrieved
        ]

        if not documents:
            return {
                "answer": "I could not find relevant information in the available documents.",
                "sources": [],
            }

        answer = self.llm_service.generate(
            query=query,
            context=documents,
        )

        sources = [
            {
                "source": metadata["source"],
                "department": metadata["department"],
                "chunk_id": metadata["chunk_id"],
            }
            for metadata in metadatas
        ]

        return {
            "answer": answer,
            "sources": sources,
        }

    @staticmethod
    def _mock_answer(query: str, documents: list[str]) -> str:
        context = "\n\n".join(documents[:3])

        return (
            "I found the following relevant information in the "
            "authorized company documents:\n\n"
            f"{context}"
        )