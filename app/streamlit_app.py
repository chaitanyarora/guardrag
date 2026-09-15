import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="FinSolve AI Assistant",
    page_icon="🤖",
    layout="wide",
)


def login(username, password):
    try:
        response = requests.get(
            f"{API_URL}/login",
            auth=(username, password),
            timeout=10,
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.RequestException:
        st.error("Could not connect to the FastAPI server.")
        return None


def ask_question(username, password, message):
    try:
        response = requests.post(
            f"{API_URL}/chat",
            params={"message": message},
            auth=(username, password),
            timeout=120,
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 401:
            st.error("Authentication failed.")

        else:
            st.error(
                f"API error: {response.status_code}"
            )

        return None

    except requests.RequestException as e:
        st.error(f"Could not connect to API: {e}")
        return None


# -----------------------------
# Session State
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

    st.title("🤖 FinSolve Internal AI Assistant")
    st.caption("Role-Based Retrieval-Augmented Generation")

    st.divider()

    with st.form("login_form"):

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

    if submitted:

        if not username or not password:
            st.warning(
                "Please enter username and password."
            )

        else:

            user = login(
                username,
                password,
            )

            if user:

                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.password = password
                st.session_state.role = user["role"]
                st.session_state.departments = user[
                    "allowed_departments"
                ]

                st.rerun()

            else:
                st.error(
                    "Invalid username or password."
                )

    st.stop()


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.title("FinSolve AI")

    st.success(
        f"Logged in as {st.session_state.username}"
    )

    st.write(
        f"**Role:** {st.session_state.role}"
    )

    st.write("**Accessible departments:**")

    for department in st.session_state.departments:
        st.write(f"• {department}")

    st.divider()

    if st.button(
        "Clear Chat",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()

    if st.button(
        "Logout",
        use_container_width=True,
    ):
        for key in [
            "authenticated",
            "username",
            "password",
            "role",
            "departments",
            "messages",
        ]:
            st.session_state[key] = (
                False
                if key == "authenticated"
                else None
                if key in ["username", "password", "role"]
                else []
            )

        st.rerun()


# -----------------------------
# Chat Interface
# -----------------------------

st.title("Internal AI Assistant")

st.caption(
    "Ask questions about authorized company documents."
)

# Display previous messages

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if message.get("sources"):

            with st.expander(
                "Sources"
            ):

                for source in message["sources"]:

                    st.write(
                        f"📄 {source['source']} "
                        f"({source['department']})"
                    )


# Chat input

prompt = st.chat_input(
    "Ask something about the company..."
)


if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching authorized documents..."
        ):

            result = ask_question(
                st.session_state.username,
                st.session_state.password,
                prompt,
            )

        if result:

            st.markdown(
                result["answer"]
            )

            sources = result.get(
                "sources",
                [],
            )

            if sources:

                with st.expander(
                    "Sources"
                ):

                    for source in sources:

                        st.write(
                            f"📄 {source['source']} "
                            f"({source['department']})"
                        )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": sources,
                }
            )