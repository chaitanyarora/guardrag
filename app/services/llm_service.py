import logging
import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Preferred models in order of capability & speed
DEFAULT_MODELS: List[str] = [
    "qwen/qwen3.8-27b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]


def _get_env_or_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieve configuration from environment variable or Streamlit secrets.
    """
    val = os.getenv(key)
    if val and val.strip():
        return val.strip()

    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key].strip()
    except Exception:
        pass

    return default


class LLMService:
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        ollama_model: str = "llama3.2:3b",
    ):
        """
        Initializes the Groq-powered LLM Service.
        - Primary: Groq Cloud API with multi-model automatic fallback
        - Fallback: Local Ollama (optional for local offline development)
        """
        self.api_key = api_key or _get_env_or_secret("GROQ_API_KEY")
        configured_model = model or _get_env_or_secret("GROQ_MODEL", DEFAULT_MODELS[0])
        
        # Build candidate models list with user-specified model first
        self.models = [configured_model] + [m for m in DEFAULT_MODELS if m != configured_model]
        self.active_model = configured_model
        self.ollama_model = ollama_model
        self.client = None

        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                logger.info(f"Initialized Groq client with primary model: {self.active_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        else:
            logger.warning(
                "GROQ_API_KEY not found in environment or secrets. "
                "LLM generation will attempt local Ollama fallback if available."
            )

    def generate(
        self,
        query: str,
        context: list[str],
    ) -> str:
        """
        Generate a strictly context-grounded response using Groq or fallback.
        """
        formatted_context = "\n\n---\n\n".join(context)

        system_instruction = (
            "You are GuardRAG, an enterprise internal AI assistant.\n\n"
            "Answer the user's question using ONLY the provided context.\n\n"
            'If the answer cannot be found in the context, say:\n'
            '"I don\'t have enough information in the authorized documents to answer that."\n\n'
            "Do not invent facts.\n"
            "Do not use outside knowledge."
        )

        user_content = f"Context:\n{formatted_context}\n\nUser question:\n{query}"

        # 1. Primary: Groq API with automatic model fallback
        if self.client:
            for model_name in self.models:
                try:
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_content},
                        ],
                        temperature=0.0,
                    )
                    self.active_model = model_name
                    content = response.choices[0].message.content
                    if content and content.strip():
                        return content
                except Exception as e:
                    logger.warning(
                        f"Groq generation failed on model '{model_name}': {e}. "
                        "Trying next model in pool..."
                    )
                    continue

        # 2. Local Ollama fallback (optional for local dev only)
        try:
            import ollama
            response = ollama.chat(
                model=self.ollama_model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_content},
                ],
                options={"temperature": 0.0},
            )
            return response["message"]["content"]
        except Exception:
            # Local Ollama not available
            pass

        # 3. Informative fallback when no API key or LLM backend responds
        if not self.api_key:
            return (
                "⚠️ **GROQ_API_KEY is missing.** Please set your Groq API key in `.env` "
                "or deployment secrets to generate AI responses.\n\n"
                "**Authorized Context Retrieved:**\n\n"
                f"{formatted_context}"
            )

        return (
            "I found the following authorized context but could not connect to the LLM backend:\n\n"
            f"{formatted_context}"
        )