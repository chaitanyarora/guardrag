from app.services.ingestion_service import (
    load_markdown_documents,
    load_hr_csv,
    split_documents,
)


documents = load_markdown_documents()

hr_documents = load_hr_csv(
    "resources/data/hr/hr_data.csv"
)

documents.extend(hr_documents)

print(f"Documents loaded: {len(documents)}")

for document in documents:
    print(
        document["department"],
        "->",
        document["source"],
    )

chunks = split_documents(documents)

print(f"\nChunks created: {len(chunks)}")

for chunk in chunks[:5]:
    print("\n---")
    print("Source:", chunk["source"])
    print("Department:", chunk["department"])
    print("Chunk ID:", chunk["chunk_id"])
    print(chunk["content"][:300])