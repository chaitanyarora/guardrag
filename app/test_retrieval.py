from services.vector_store import VectorStore


def main():
    vector_store = VectorStore()

    query = "What is the engineering architecture?"

    allowed_departments = [
    "engineering",
    "general",
]

    results = vector_store.search(
        query=query,
        allowed_departments=allowed_departments,
        n_results=5,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print(f"\nQuery: {query}\n")

    for index, (document, metadata, distance) in enumerate(
    zip(documents, metadatas, distances),
    start=1,
):
        print(f"--- Result {index} ---")
        print("Distance:", distance)
        print("Source:", metadata["source"])
        print("Department:", metadata["department"])
        print("Chunk:", metadata["chunk_id"])
        print("Content:")
        print(document[:500])
        print()


if __name__ == "__main__":
    main()