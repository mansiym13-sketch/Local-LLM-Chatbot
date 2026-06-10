# 🤖 Local LLM Chatbot

A powerful, privacy-first AI chatbot that runs completely on your local machine using open-source Large Language Models (LLMs). This project provides a simple, interactive chat interface leveraging Ollama and Streamlit, ensuring complete data privacy, low latency, and offline accessibility. 

## 🚀 Features

* **💬 Interactive Web Interface:** Built with Streamlit for a clean, user-friendly experience.
* **🧠 Local Execution:** Runs models completely locally using Ollama-supported models.
* **🔒 100% Privacy:** No cloud APIs required. Your data never leaves your machine.
* **⚡ Fast Generation:** Low latency responses directly from your hardware.
* **📜 Conversation Memory:** Maintains context across the chat session for natural interactions.
* **📚 RAG Support:** Includes Retrieval-Augmented Generation (RAG) capabilities to anchor responses in local data.
* **🎯 Multi-Model Support:** Easily switch between popular open-source LLMs like Llama 3, Mistral, Gemma, and more.

## 🛠️ Tech Stack

* **Language:** Python 3.9+
* **Frontend:** Streamlit
* **LLM Engine:** Ollama
* **Framework:** LangChain
* **Models:** Llama 3, Mistral, Gemma, etc.

## 📂 Project Structure

```text
Local-LLM-Chatbot/
│
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
📋 Prerequisites
Before running the project, ensure you have the following installed on your system:

Python 3.9 or higher

Ollama installed and running

Install Ollama & Download Models
First, download and install Ollama from their official website. Once installed, open your terminal and pull your preferred model:

Bash
# Verify installation
ollama --version

# Pull Llama 3 (or swap for 'mistral', 'gemma', etc.)
ollama pull llama3
⚙️ Installation & Setup
1. Clone the Repository

Bash
git clone [https://github.com/mansiym13-sketch/Local-LLM-Chatbot.git](https://github.com/mansiym13-sketch/Local-LLM-Chatbot.git)
cd Local-LLM-Chatbot
2. Create and Activate a Virtual Environment

Bash
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on Linux / Mac:
source venv/bin/activate
3. Install Dependencies

Bash
pip install -r requirements.txt
▶️ Running the Application
1. Start the Ollama Server
(Make sure Ollama is running in the background. You can usually start it by opening the Ollama application or running this in a separate terminal:)

Bash
ollama serve
2. Run the Chatbot

Bash
streamlit run app.py
The application will automatically open in your default browser at http://localhost:8501.

🎯 Usage
Open the web interface via the localhost URL.

Select your desired local model (e.g., Llama 3).

Type your query into the chat box.

The chatbot will process the prompt locally and generate AI responses in real time.

🔒 Privacy Benefits
Because this application utilizes local models through Ollama:

No external server pinging: Zero data is transmitted to third-party companies.

No API Keys: Completely free to run once set up.

Full Data Control: You have absolute ownership of your conversation history and uploaded documents.

Offline Mode: Works perfectly without an internet connection (after the initial model download).
