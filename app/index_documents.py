from app.services.ingestion_service import (
    load_markdown_documents,
    load_hr_csv,
    split_documents,
)

from app.services.vector_store import VectorStore


def main():
    print("Loading documents...")

    documents = load_markdown_documents()

    hr_documents = load_hr_csv(
        "resources/data/hr/hr_data.csv"
    )

    documents.extend(hr_documents)

    print(f"Loaded {len(documents)} documents.")

    chunks = split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    print("Creating/updating ChromaDB...")

    vector_store = VectorStore()

    vector_store.add_documents(chunks)

    print("Indexing complete.")


if __name__ == "__main__":
    main()