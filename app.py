"""
Secure Enterprise Local-LLM Portal
-----------------------------------
A fully private, on-premise Retrieval-Augmented Generation (RAG) knowledge
platform built on Streamlit + LangChain + Ollama + Chroma.

All inference, embedding, and vector-storage operations run entirely on
local infrastructure via Ollama — no document content or chat data ever
leaves the host machine.
"""

import os
import time
import uuid
import shutil
import tempfile
import logging
from typing import List

import streamlit as st
import ollama

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

# --------------------------------------------------------------------------
# Logging (audit trail — local only, never transmitted)
# --------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("secure_enterprise_portal")

# --------------------------------------------------------------------------
# Constants / Configuration
# --------------------------------------------------------------------------
AVAILABLE_MODELS = ["llama3", "mistral"]

PERSIST_ROOT = os.path.join(tempfile.gettempdir(), "secure_enterprise_portal", "chroma_store")

SYSTEM_PROMPT_TEMPLATE = """You are a Secure Enterprise Knowledge Assistant operating under a strict \
anti-hallucination protocol. You must ground every claim you make strictly and exclusively \
inside the CONTEXT provided below, which was retrieved from documents uploaded by an \
authorized enterprise user.

RULES OF ENGAGEMENT (NON-NEGOTIABLE):
1. Answer ONLY using facts that are explicitly present in, or can be directly and reasonably \
   inferred from, the CONTEXT below.
2. If the CONTEXT does not contain enough information to answer the question with confidence, \
   you MUST respond with: "I cannot verify this information from the provided document(s)." \
   Do not guess, speculate, or fill gaps with outside knowledge.
3. Do NOT use any prior/general knowledge to supplement, contradict, or extend the CONTEXT.
4. When you do answer, cite the relevant facts concisely and avoid inventing figures, names, \
   dates, or clauses that do not appear in the CONTEXT.
5. Maintain a professional, precise, and neutral enterprise tone at all times.

CONTEXT:
{context}
"""

NO_DOC_SYSTEM_PROMPT = """You are a Secure Enterprise Knowledge Assistant. No document has been \
uploaded for this session, so you are operating in general local-assistant mode. Be helpful, \
concise, and professional. If the user asks about specific internal documents, remind them to \
upload a PDF via the sidebar so you can ground your answers in verified enterprise content."""

# --------------------------------------------------------------------------
# Page configuration
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Secure Enterprise Local-LLM Portal",
    page_icon="🔒",
    layout="wide",
)

# --------------------------------------------------------------------------
# Session State Initialization (thread-safe, per-session chat memory)
# --------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages: List[dict] = []

if "vectordb" not in st.session_state:
    st.session_state.vectordb = None

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "indexed_files" not in st.session_state:
    st.session_state.indexed_files: List[str] = []

if "embedding_model_used" not in st.session_state:
    st.session_state.embedding_model_used = None


# --------------------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------------------
def get_persist_directory(session_id: str) -> str:
    """Return the on-disk Chroma persistence path for this session."""
    path = os.path.join(PERSIST_ROOT, session_id)
    os.makedirs(path, exist_ok=True)
    return path


def check_ollama_model_available(model_name: str) -> bool:
    """Verify that a given model is pulled and available in the local Ollama runtime."""
    try:
        local_models = ollama.list()
        names = [m.get("model", m.get("name", "")) for m in local_models.get("models", [])]
        return any(model_name in n for n in names)
    except Exception as exc:  # Ollama daemon unreachable, etc.
        logger.warning("Could not query local Ollama daemon: %s", exc)
        return False


def ingest_pdf(uploaded_file, embedding_model: str, session_id: str) -> Chroma:
    """
    Ingest an uploaded PDF into a persistent, on-disk Chroma vector store using
    fully local, on-device embeddings generated via Ollama.
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name

        loader = PyPDFLoader(tmp_path)
        raw_docs: List[Document] = loader.load()

        if not raw_docs:
            raise ValueError("No extractable text content was found in the uploaded PDF.")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_documents(raw_docs)

        for chunk in chunks:
            chunk.metadata["source_file"] = uploaded_file.name

        embeddings = OllamaEmbeddings(model=embedding_model)

        persist_directory = get_persist_directory(session_id)

        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name=f"enterprise_docs_{session_id}",
        )

        logger.info(
            "Ingested '%s' into Chroma (%d chunks, embedding model: %s)",
            uploaded_file.name,
            len(chunks),
            embedding_model,
        )
        return vectordb
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def format_retrieved_context(docs: List[Document]) -> str:
    """Format retrieved chunks into a clearly delimited context block for the prompt."""
    if not docs:
        return "No relevant context was retrieved from the uploaded document(s)."

    formatted_blocks = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source_file", "unknown_document")
        page = doc.metadata.get("page", "n/a")
        formatted_blocks.append(
            f"[Chunk {i} | source: {source} | page: {page}]\n{doc.page_content.strip()}"
        )
    return "\n\n".join(formatted_blocks)


def build_prompt_messages(context: str, chat_history: List[dict], question: str) -> List[dict]:
    """
    Construct the final message payload sent to Ollama, combining the enterprise
    guardrail system prompt with recent conversational turns for multi-turn memory.
    """
    system_template = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT_TEMPLATE)]
    )
    rendered_system = system_template.format_messages(context=context)[0].content

    messages = [{"role": "system", "content": rendered_system}]

    # Include recent conversational turns (excluding the current question) for memory continuity.
    for turn in chat_history[-10:]:
        messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({"role": "user", "content": question})
    return messages


def build_no_doc_messages(chat_history: List[dict], question: str) -> List[dict]:
    """Construct message payload for general-mode (no document uploaded) queries."""
    messages = [{"role": "system", "content": NO_DOC_SYSTEM_PROMPT}]
    for turn in chat_history[-10:]:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": question})
    return messages


def clear_session_vector_store():
    """Wipe the on-disk Chroma collection for the current session."""
    st.session_state.vectordb = None
    st.session_state.retriever = None
    st.session_state.indexed_files = []
    session_dir = get_persist_directory(st.session_state.session_id)
    if os.path.isdir(session_dir):
        shutil.rmtree(session_dir, ignore_errors=True)


# --------------------------------------------------------------------------
# Sidebar — Control Matrix
# --------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Control Matrix")

    st.markdown("##### Foundational Model")
    selected_model = st.selectbox(
        "Active Inference Model",
        AVAILABLE_MODELS,
        index=0,
        help="Hot-swap the local Ollama model powering both chat generation and embeddings.",
    )

    model_available = check_ollama_model_available(selected_model)
    if model_available:
        st.success(f"✅ '{selected_model}' is available locally.")
    else:
        st.warning(
            f"⚠️ '{selected_model}' was not detected in the local Ollama registry. "
            f"Run `ollama pull {selected_model}` before generating."
        )

    st.divider()

    st.markdown("##### Document Ingestion")
    uploaded_file = st.file_uploader(
        "Upload Enterprise PDF",
        type="pdf",
        help="Document is processed entirely on-device. Nothing is uploaded externally.",
    )

    if uploaded_file is not None and uploaded_file.name not in st.session_state.indexed_files:
        with st.spinner(f"🔐 Indexing '{uploaded_file.name}' locally via {selected_model} embeddings..."):
            try:
                vectordb = ingest_pdf(uploaded_file, "nomic-embed-text", st.session_state.session_id)
                st.session_state.vectordb = vectordb
                st.session_state.retriever = vectordb.as_retriever(search_kwargs={"k": 3})
                st.session_state.indexed_files.append(uploaded_file.name)
                st.session_state.embedding_model_used = "nomic-embed-text"
                st.success(f"📄 '{uploaded_file.name}' indexed and ready for retrieval.")
            except Exception as exc:
                logger.exception("PDF ingestion failed")
                st.error(f"❌ Ingestion failed: {exc}")

    if st.session_state.indexed_files:
        st.markdown("**Indexed Documents:**")
        for fname in st.session_state.indexed_files:
            st.caption(f"📎 {fname}")

        st.markdown("### ⚙️ Pipeline Configuration")

        st.caption(f"Chat Model: {selected_model}")
        st.caption(f"Embedding Model: {st.session_state.embedding_model_used}")
        st.caption("Vector Store: ChromaDB")
        st.caption(f"Indexed Documents: {len(st.session_state.indexed_files)}")

        if st.button("🧹 Purge Vector Store"):
            clear_session_vector_store()
            st.rerun()

    st.divider()

    rag_status = "🟢 RAG Active" if st.session_state.retriever else "⚪ General Mode"
    st.markdown(f"**Pipeline Status:** {rag_status}")

    st.divider()

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    st.caption("🔒 All inference, embeddings, and storage remain fully on-premise.")

# --------------------------------------------------------------------------
# Main Panel
# --------------------------------------------------------------------------
st.title("🔒 Secure Enterprise Local-LLM Portal")
st.caption(
    f"Architecture: **{selected_model}** &nbsp;|&nbsp; "
    f"Retrieval Mode: **{'RAG (Chroma + Ollama Embeddings)' if st.session_state.retriever else 'Direct Inference'}**"
)

st.divider()

# Render existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "metrics" in message:
            st.caption(message["metrics"])

# --------------------------------------------------------------------------
# Chat Input & Generation
# --------------------------------------------------------------------------
prompt = st.chat_input("Ask a question about your enterprise documents, or chat generally...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        metrics_placeholder = st.empty()
        full_response = ""

        history_without_current = st.session_state.messages[:-1]

        retrieval_mode = st.session_state.retriever is not None

        try:
            if retrieval_mode:
                retrieved_docs = st.session_state.retriever.invoke(prompt)
                context = format_retrieved_context(retrieved_docs)
                messages_payload = build_prompt_messages(context, history_without_current, prompt)
            else:
                messages_payload = build_no_doc_messages(history_without_current, prompt)

            start_time = time.perf_counter()

            stream = ollama.chat(
                model=selected_model,
                messages=messages_payload,
                stream=True,
            )

            for chunk in stream:
                token = chunk.get("message", {}).get("content", "")
                full_response += token
                placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

            end_time = time.perf_counter()
            latency = end_time - start_time

            metrics_text = (
                f"⚡ Performance Metrics: Inference Latency: {latency:.2f}s "
                f"| Architecture: {selected_model} "
                f"| Mode: {'RAG' if retrieval_mode else 'Direct'}"
            )
            metrics_placeholder.caption(metrics_text)

        except Exception as exc:
            logger.exception("Generation failed")
            error_message = (
                f"❌ Generation failed: {exc}\n\n"
                f"Verify that the Ollama daemon is running and that '{selected_model}' "
                f"has been pulled locally (`ollama pull {selected_model}`)."
            )
            placeholder.markdown(error_message)
            full_response = error_message
            metrics_text = f"⚡ Performance Metrics: Inference Latency: N/A | Architecture: {selected_model}"
            metrics_placeholder.caption(metrics_text)

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response, "metrics": metrics_text}
    )
