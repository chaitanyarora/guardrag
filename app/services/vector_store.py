from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHROMA_PATH = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "finsolve_documents"


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME
        )

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def add_documents(self, chunks):

        documents = []
        metadatas = []
        ids = []

        for chunk in chunks:
            documents.append(chunk["content"])

            metadata = {
                "source": chunk["source"],
                "department": chunk["department"],
                "chunk_id": chunk["chunk_id"],
                "allowed_roles": ",".join(
                    self._get_allowed_roles(
                        chunk["department"]
                    )
                ),
            }

            if "employee_id" in chunk:
                metadata["employee_id"] = chunk["employee_id"]

            metadatas.append(metadata)

            if "employee_id" in chunk:
                chunk_id = (
                    f'{chunk["source"]}_'
                    f'{chunk["employee_id"]}_'
                    f'{chunk["chunk_id"]}'
                )
            else:
                chunk_id = (
                    f'{chunk["source"]}_'
                    f'{chunk["chunk_id"]}'
                )

            ids.append(chunk_id)

        embeddings = self.embedding_model.encode(
            documents
        ).tolist()

        self.collection.upsert(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

    def search(
    self,
    query: str,
    allowed_departments: list[str],
    n_results: int = 5,
):
        query_embedding = self.embedding_model.encode(
            [query]
        ).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where={
                "department": {
                    "$in": allowed_departments
                }
            },
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        return results

    @staticmethod
    def _get_allowed_roles(department):
        permissions = {
            "finance": [
                "finance",
                "executive",
            ],
            "marketing": [
                "marketing",
                "executive",
            ],
            "hr": [
                "hr",
                "executive",
            ],
            "engineering": [
                "engineering",
                "executive",
            ],
            "general": [
                "finance",
                "marketing",
                "hr",
                "engineering",
                "executive",
                "employee",
            ],
        }

        return permissions.get(
            department,
            [],
        )