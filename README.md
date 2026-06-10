# 🤖 Local LLM Chatbot

A powerful AI chatbot that runs completely on your local machine using open-source Large Language Models (LLMs). This project provides a simple and interactive chat interface while ensuring privacy, low latency, and offline accessibility.

## 🚀 Features

- 💬 Interactive chatbot interface
- 🧠 Runs locally using Ollama-supported models
- 🔒 Complete privacy (no cloud API required)
- ⚡ Fast response generation
- 🌐 User-friendly web interface
- 📜 Maintains conversation context
- 🎯 Supports multiple open-source LLMs

## 🛠️ Tech Stack

- Python
- Streamlit
- Ollama
- LangChain (if used)
- Local LLM Models (Llama 3, Mistral, Gemma, etc.)

## 📂 Project Structure


Local-LLM-Chatbot/
│
├── app.py # Main application
├── requirements.txt # Dependencies
└── README.md


## 📋 Prerequisites

Before running the project, make sure you have:

- Python 3.9+
- Ollama installed

### Install Ollama

Visit:

:contentReference[oaicite:0]{index=0}

Verify installation:

```bash
ollama --version
📥 Download a Model

Pull your preferred model:

ollama pull llama3

or

ollama pull mistral
⚙️ Installation
1. Clone the Repository
git clone https://github.com/mansiym13-sketch/Local-LLM-Chatbot.git
cd Local-LLM-Chatbot
2. Create a Virtual Environment
python -m venv venv

Activate it:

Windows

venv\Scripts\activate

Linux / Mac

source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
▶️ Run the Application

Start Ollama:

ollama serve

Run the chatbot:

streamlit run app.py

The application will be available at:

http://localhost:8501
🎯 Usage
Open the web interface.
Type your query.
The chatbot sends the prompt to the local LLM.
Receive AI-generated responses in real time.
🔒 Privacy Benefits

Since the model runs locally:

No data is sent to external servers.
No API keys required.
Full control over conversations.
Works offline after model download.
