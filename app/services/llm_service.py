# from ollama import chat


# class LLMService:
#     def __init__(self, model: str = "llama3.2:1b"):
#         self.model = model

#     def generate(
#         self,
#         query: str,
#         context: list[str],
#     ) -> str:

#         formatted_context = "\n\n---\n\n".join(context)

#         prompt = f"""
# You are FinSolve Technologies' internal AI assistant.

# Answer the user's question using ONLY the provided context.

# If the answer cannot be found in the context, say:
# "I don't have enough information in the authorized documents to answer that."

# Do not invent facts.
# Do not use outside knowledge.

# Context:
# {formatted_context}

# User question:
# {query}

# Answer:
# """

#         response = chat(
#             model=self.model,
#             messages=[
#                 {
#                     "role": "user",
#                     "content": prompt,
#                 }
#             ],
#         )

#         return response["message"]["content"]

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load variables from .env file into environment
load_dotenv()
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMService:
    def __init__(
        self,
        model: str = "llama3-8b-8192",
        api_key: str | None = None,
    ):
        self.model = model
        self.client = OpenAI(
            api_key=api_key or os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )

    def generate(
        self,
        query: str,
        context: list[str],
    ) -> str:
        formatted_context = "\n\n---\n\n".join(context)

        system_instruction = (
            "You are FinSolve Technologies' internal AI assistant.\n\n"
            "Answer the user's question using ONLY the provided context.\n\n"
            'If the answer cannot be found in the context, say:\n'
            '"I don\'t have enough information in the authorized documents to answer that."\n\n'
            "Do not invent facts.\n"
            "Do not use outside knowledge."
        )

        user_content = f"Context:\n{formatted_context}\n\nUser question:\n{query}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content},
            ],
            temperature=0.0,  # Kept at 0.0 for strict factual RAG adherence
        )

        return response.choices[0].message.content