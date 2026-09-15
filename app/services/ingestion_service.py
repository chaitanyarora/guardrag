from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
import pandas as pd


DATA_DIR = Path("resources/data")


def load_markdown_documents():
    documents = []

    for file_path in DATA_DIR.rglob("*.md"):
        department = file_path.parent.name

        content = file_path.read_text(encoding="utf-8")

        documents.append(
            {
                "content": content,
                "source": file_path.name,
                "department": department,
            }
        )

    return documents


def load_hr_csv(csv_path: str):
    df = pd.read_csv(csv_path)

    documents = []

    for _, row in df.iterrows():
        content = f"""
Employee ID: {row['employee_id']}
Name: {row['full_name']}
Role: {row['role']}
Department: {row['department']}
Email: {row['email']}
Location: {row['location']}
Date of Joining: {row['date_of_joining']}
Manager ID: {row['manager_id']}
Salary: {row['salary']}
Leave Balance: {row['leave_balance']}
Leaves Taken: {row['leaves_taken']}
Attendance: {row['attendance_pct']}%
Performance Rating: {row['performance_rating']}
Last Review Date: {row['last_review_date']}
""".strip()

        documents.append(
            {
                "content": content,
                "source": "hr_data.csv",
                "department": "hr",
                "employee_id": str(row["employee_id"]),
            }
        )

    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )

    chunks = []

    for document in documents:
        split_content = splitter.split_text(document["content"])

        for index, content in enumerate(split_content):
            chunk = {
                "content": content,
                "source": document["source"],
                "department": document["department"],
                "chunk_id": index,
            }

            # Preserve employee ID for HR records
            if "employee_id" in document:
                chunk["employee_id"] = document["employee_id"]

            chunks.append(chunk)

    return chunks