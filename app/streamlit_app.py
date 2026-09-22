import os
import sys
from pathlib import Path

# Add repository root to sys.path so 'app.*' imports work on Streamlit Community Cloud
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import requests
import streamlit as st
from app.services.auth_service import users_db
from app.services.rbac_service import get_allowed_departments
from app.services.rag_service import RAGService
from app.index_documents import main as index_documents_if_needed

# Determine if a remote FastAPI server is configured
API_URL = os.getenv("API_URL", "").rstrip("/")


st.set_page_config(
    page_title="GuardRAG: Enterprise AI Assistant",
    page_icon="🛡️",
    layout="wide",
)


@st.cache_resource(show_spinner="Initializing GuardRAG Vector Knowledge Base...")
def get_rag_service():
    """
    Initializes RAGService and ensures the ChromaDB vector database is indexed.
    """
    from app.services.vector_store import VectorStore
    vs = VectorStore()
    try:
        if vs.collection.count() == 0:
            index_documents_if_needed()
    except Exception:
        index_documents_if_needed()
    return RAGService()


def login(username, password):
    # 1. Try remote FastAPI server if configured
    if API_URL:
        try:
            response = requests.get(
                f"{API_URL}/login",
                auth=(username, password),
                timeout=5,
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return None
        except Exception:
            pass

    # 2. In-Process Authentication fallback
    user = users_db.get(username)
    if user and user["password"] == password:
        return {
            "message": f"Welcome {username}!",
            "role": user["role"],
            "allowed_departments": get_allowed_departments(user["role"]),
        }

    return None


def ask_question(username, password, message, role):
    # 1. Try remote FastAPI server if configured
    if API_URL:
        try:
            response = requests.post(
                f"{API_URL}/chat",
                params={"message": message},
                auth=(username, password),
                timeout=120,
            )
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass

    # 2. In-Process RAG Service
    rag_service = get_rag_service()
    result = rag_service.answer(
        query=message,
        role=role,
    )
    return {
        "user": username,
        "role": role,
        "message": message,
        "answer": result["answer"],
        "sources": result.get("sources", []),
    }


# -----------------------------
# Session State Initialization
# -----------------------------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = None

if "password" not in st.session_state:
    st.session_state.password = None

if "role" not in st.session_state:
    st.session_state.role = None

if "departments" not in st.session_state:
    st.session_state.departments = []

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# Login Screen
# -----------------------------

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>🛡️ GuardRAG</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #94A3B8;'>Enterprise Role-Based Access Control (RBAC) Knowledge Retrieval Assistant</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("🔐 Secure Sign In")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if not username or not password:
                st.warning("Please enter username and password.")
            else:
                user = login(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.password = password
                    st.session_state.role = user["role"]
                    st.session_state.departments = user["allowed_departments"]
                    st.rerun()
                else:
                    st.error("Invalid credentials. Use one of the demo accounts on the right.")

    with col2:
        st.subheader("👥 Quick Demo Personas")
        st.caption("Click a persona below to auto-fill credentials and test RBAC data boundaries:")

        demo_accounts = [
            ("Tony (Engineering)", "Tony", "password123", "engineering", "Access to Architecture & Specs"),
            ("Natasha (HR)", "Natasha", "hrpass123", "hr", "Access to Salaries & Employee Reviews"),
            ("Sam (Finance)", "Sam", "financepass", "finance", "Access to P&L & Financial Reports"),
            ("Bruce (Marketing)", "Bruce", "securepass", "marketing", "Access to Campaign Metrics & Growth"),
        ]

        for label, u, p, role, desc in demo_accounts:
            col_btn, col_desc = st.columns([1, 1])
            with col_btn:
                if st.button(f"👤 {label}", key=f"btn_{u}", use_container_width=True):
                    user = login(u, p)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.username = u
                        st.session_state.password = p
                        st.session_state.role = user["role"]
                        st.session_state.departments = user["allowed_departments"]
                        st.rerun()
            with col_desc:
                st.markdown(f"<small style='color: #64748B;'>{desc}</small>", unsafe_allow_html=True)

    st.stop()

else:
    # -----------------------------
    # Authenticated Sidebar
    # -----------------------------

    role_display = (st.session_state.role or "GUEST").upper()
    username_display = st.session_state.username or "Guest"

    with st.sidebar:
        st.title("🛡️ GuardRAG")
        st.caption("Enterprise Knowledge Base")
        st.divider()

        st.success(f"**Logged in as:** `{username_display}`")
        st.info(f"**Assigned Role:** `{role_display}`")

        st.write("**Allowed Data Partitions:**")
        for department in st.session_state.departments:
            st.markdown(f"- 📁 `{department}`")

        st.divider()

        if st.button("🧹 Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        if st.button("🚪 Logout", use_container_width=True):
            for key in ["authenticated", "username", "password", "role", "departments", "messages"]:
                st.session_state[key] = (
                    False if key == "authenticated"
                    else None if key in ["username", "password", "role"]
                    else []
                )
            st.rerun()


    # -----------------------------
    # Main Chat Interface
    # -----------------------------

    st.title("💬 Authorized Assistant")
    st.caption(
        f"Querying company knowledge base with **{role_display}** permissions."
    )

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("📑 Verified Source Citations"):
                    for source in message["sources"]:
                        st.markdown(
                            f"- 📄 **Document:** `{source['source']}` | **Department:** `{source['department']}` | **Chunk:** `{source['chunk_id']}`"
                        )

    # Chat input
    prompt = st.chat_input("Ask a question about internal documents...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving authorized documents & generating answer..."):
                result = ask_question(
                    username=st.session_state.username,
                    password=st.session_state.password,
                    message=prompt,
                    role=st.session_state.role,
                )

            if result:
                st.markdown(result["answer"])
                sources = result.get("sources", [])

                if sources:
                    with st.expander("📑 Verified Source Citations"):
                        for source in sources:
                            st.markdown(
                                f"- 📄 **Document:** `{source['source']}` | **Department:** `{source['department']}` | **Chunk:** `{source['chunk_id']}`"
                            )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": sources,
                    }
                )