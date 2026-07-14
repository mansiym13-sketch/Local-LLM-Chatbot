# 🤖 Secure Enterprise Local-LLM Portal

A fully offline, enterprise-grade Retrieval-Augmented Generation (RAG) chatbot built using **Ollama**, **ChromaDB**, **Streamlit**, and **LangChain**. The application enables users to upload enterprise PDF documents, index them locally, and ask intelligent questions without sending any data to external APIs.

> 🔒 100% Local • 📄 PDF RAG • 🧠 Local LLMs • ⚡ ChromaDB • 🚀 Streamlit

---

## ✨ Features

- 🖥️ Fully offline AI assistant powered by Ollama
- 📄 Upload and chat with enterprise PDF documents
- 🧠 Retrieval-Augmented Generation (RAG)
- 🔍 Semantic search using local embeddings
- 💾 ChromaDB vector database
- 🔄 Supports multiple local LLMs (Llama 3 & Mistral)
- 📚 Automatic document chunking and indexing
- 🔒 Privacy-first architecture (no cloud APIs)
- 🧹 Clear chat history
- 🗑️ Purge vector database
- 📊 Pipeline status monitoring
- ⚡ Automatic switch between Direct Inference and RAG mode

---

## 🏗️ Architecture

```
                PDF Upload
                     │
                     ▼
             Document Loader
                     │
                     ▼
            Text Chunking
                     │
                     ▼
      nomic-embed-text Embeddings
                     │
                     ▼
               ChromaDB
                     │
         ┌───────────┴───────────┐
         │                       │
      Retrieved Context      User Query
         │                       │
         └───────────┬───────────┘
                     ▼
             Ollama (Llama3/Mistral)
                     │
                     ▼
              Generated Response
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| Frontend | Streamlit |
| LLM Runtime | Ollama |
| Models | Llama 3, Mistral |
| Embedding Model | nomic-embed-text |
| Vector Database | ChromaDB |
| Framework | LangChain |
| PDF Processing | PyPDFLoader |
| Environment | Python Virtual Environment |

---

## 📂 Project Structure

```
Local-LLM-Chatbot/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── chroma_db/           # Generated automatically
├── vector_store/        # Generated automatically
└── chat_history.json    # Generated automatically
```

---

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/mansiym13-sketch/Local-LLM-Chatbot.git
cd Local-LLM-Chatbot
```

---

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Install Ollama

Download from:

https://ollama.com/download

---

### 5. Pull Required Models

```bash
ollama pull llama3
```

```bash
ollama pull mistral
```

```bash
ollama pull nomic-embed-text
```

---

### 6. Start Ollama

```bash
ollama serve
```

---

### 7. Launch Application

```bash
streamlit run app.py
```

---

## 📖 Usage

1. Launch the application.
2. Select your preferred LLM.
3. Upload an enterprise PDF.
4. Wait for document indexing.
5. Ask natural language questions.
6. Receive context-aware responses generated entirely on your machine.

---

## 🔄 Pipeline Modes

### General Mode

Used when:

- No document has been uploaded
- No relevant context is found

Response generated directly from the selected LLM.

---

### RAG Mode

Activated automatically after document indexing.

Workflow:

```
User Question
      │
      ▼
Similarity Search
      │
      ▼
Retrieve Relevant Chunks
      │
      ▼
Context + Prompt
      │
      ▼
Local LLM
      │
      ▼
Grounded Answer
```

---

## 🔒 Privacy

- No OpenAI API required
- No internet needed after model download
- All inference happens locally
- Documents never leave your computer
- Enterprise-ready local deployment

---



## 🎯 Future Improvements

- Conversation memory
- Multiple document support
- Citation highlighting
- Source page references
- Hybrid search (BM25 + Vector)
- Authentication
- Docker deployment
- Dark mode
- REST API support

---

## 👩‍💻 Author

**Mansi Ahirrao**

Final Year Computer Science Engineering (Big Data & Cloud Engineering)

- AWS Certified Cloud Practitioner and AI Practitioner 
- AI • ML • Cloud • DevOps
- Python | FastAPI | Docker | Kubernetes | Ollama

GitHub:
https://github.com/mansiym13-sketch

LinkedIn: https://www.linkedin.com/in/mansi-ahirrao-7652992a8/

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!
