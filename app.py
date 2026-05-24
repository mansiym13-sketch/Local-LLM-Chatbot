import streamlit as st
import ollama
import json
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import tempfile

CHAT_FILE = "chat_history.json"

# Load chat history
def load_chat():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Save chat history
def save_chat(messages):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4)

st.set_page_config(
    page_title="LocalGPT",
    page_icon="🤖",
    layout="wide"
)

# Models
models = [
    "qwen2.5:1.5b",
    "tinyllama"
]

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = load_chat()

if "vectordb" not in st.session_state:
    st.session_state.vectordb = None

# Sidebar
with st.sidebar:
    st.title("⚙️ LocalGPT")

    selected_model = st.selectbox(
        "Choose AI Model",
        models
    )

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type="pdf"
    )

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name

        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = splitter.split_documents(docs)

        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        vectordb = Chroma.from_documents(
            chunks,
            embeddings
        )

        st.session_state.vectordb = vectordb
        st.success("PDF loaded successfully!")

    if st.button("🗑️ Clear Chat"):
      st.session_state.messages = []
      save_chat([])
      st.rerun()

st.title("🤖 LocalGPT")
st.caption(f"Running: {selected_model}")

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask anything...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    save_chat(st.session_state.messages)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        # RAG search
        if st.session_state.vectordb:
            docs = st.session_state.vectordb.similarity_search(
                prompt,
                k=3
            )

            context = "\n".join(
                [doc.page_content for doc in docs]
            )

            prompt_with_context = f"""
Use the following PDF context to answer.

Context:
{context}

Question:
{prompt}
"""

            stream = ollama.chat(
                model=selected_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt_with_context
                    }
                ],
                stream=True
            )
        else:
            stream = ollama.chat(
                model=selected_model,
                messages=st.session_state.messages,
                stream=True
            )

        for chunk in stream:
            full_response += chunk["message"]["content"]
            placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )