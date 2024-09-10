# Gemini + LangChain Enterprise Chatbot on Google Cloud Platform (GCP)

An enterprise-ready conversational AI application built with **Google Cloud Vertex AI**, **Gemini (1.5 Flash / 1.5 Pro / 2.0 Flash)**, **LangChain**, and **Python 3.11+**.

This project includes:
- **Dual Interfaces**: An interactive **CLI terminal client** (`cli.py`) and a modern **Streamlit Web UI** (`app.py`).
- **Real-Time Streaming**: Low-latency token-by-token streaming responses.
- **Conversational Memory**: Multi-turn contextual chat history using LangChain's `RunnableWithMessageHistory`.
- **Cloud Run Ready**: Containerized with a multi-stage `Dockerfile` and automated health checks.

---

## Architecture Overview

```
User (Browser / CLI)
       │
       ▼
 ┌─────────────────────────────────────────────────────────┐
 │ Streamlit Web App (`app.py`) / Terminal CLI (`cli.py`)  │
 └────────────────────────────┬────────────────────────────┘
                              │
                              ▼
 ┌─────────────────────────────────────────────────────────┐
 │ LangChain Conversational Chain (`chatbot.py`)           │
 │  - ChatPromptTemplate + System Persona                  │
 │  - RunnableWithMessageHistory (Session Management)       │
 └────────────────────────────┬────────────────────────────┘
                              │
                              ▼
 ┌─────────────────────────────────────────────────────────┐
 │ Google Cloud Vertex AI Client (`ChatVertexAI`)          │
 │  - Authentication: Application Default Credentials (ADC)│
 │  - Model: gemini-1.5-flash / gemini-1.5-pro             │
 └────────────────────────────┬────────────────────────────┘
                              │
                              ▼
                Google Cloud Vertex AI API
```

---

## Project Structure

```
gemini-langchain-chatbot/
├── .env.example             # Template for environment variables
├── .gitignore               # Ignored files (secrets, virtualenv, pycache)
├── Dockerfile               # Production container definition for Cloud Run
├── README.md                # Comprehensive documentation and execution guide
├── app.py                   # Streamlit web application with streaming UI
├── chatbot.py               # Core LangChain + Vertex AI conversational engine
├── cli.py                   # Terminal interactive CLI chatbot
├── config.py                # Dataclass settings and environment loader
├── requirements.txt         # Pinned Python package dependencies
└── utils/
    ├── __init__.py
    └── auth.py              # GCP credential verification and project resolution
```

---

## Step-by-Step Execution Guide

### Step 1: Google Cloud Platform (GCP) Setup

1. **Install and Update Google Cloud SDK (`gcloud`)**:
   Ensure `gcloud` CLI is installed and up to date:
   ```bash
   gcloud components update
   ```

2. **Create or Select a GCP Project**:
   Set your active project:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```
   Verify the currently active project:
   ```bash
   gcloud config get-value project
   ```

3. **Enable Required GCP APIs**:
   Enable the **Vertex AI** API (and Cloud Run API for deployment):
   ```bash
   gcloud services enable aiplatform.googleapis.com run.googleapis.com
   ```

4. **Configure Authentication**:
   - **For Local Development (Application Default Credentials)**:
     This allows LangChain to communicate securely with Vertex AI on your workstation:
     ```bash
     gcloud auth application-default login
     ```
   - **For Production (Cloud Run / GKE / Service Account)**:
     Create a dedicated Service Account and grant it the **Vertex AI User** (`roles/aiplatform.user`) role:
     ```bash
     # 1. Create Service Account
     gcloud iam service-accounts create gemini-chatbot-sa \
       --description="Service Account for Gemini Chatbot" \
       --display-name="Gemini Chatbot SA"

     # 2. Assign Vertex AI User role
     gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:gemini-chatbot-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/aiplatform.user"
     ```

---

### Step 2: Create Python Virtual Environment & Install Dependencies

1. **Navigate to the project folder**:
   ```bash
   cd /Users/khansaddam/Workspaces/GenAI/gemini-langchain-chatbot
   ```

2. **Create an isolated virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   .venv/bin/pip install --upgrade pip
   .venv/bin/pip install -r requirements.txt
   ```

---

### Step 3: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and set your GCP Project ID and preferences:
   ```dotenv
   GOOGLE_CLOUD_PROJECT=your-gcp-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   GEMINI_MODEL=gemini-1.5-flash
   MODEL_TEMPERATURE=0.7
   MAX_OUTPUT_TOKENS=2048
   ```

---

### Step 4: Run the Interactive CLI Chatbot

To start chatting immediately inside your terminal with live token streaming:

```bash
source .venv/bin/activate
python cli.py
```

**CLI Commands**:
- Type your question and press `Enter`.
- Type `clear` or `reset` to wipe conversation history.
- Type `exit` or `quit` to exit.

---

### Step 5: Run the Streamlit Web Application

To launch the full browser interface with dynamic model switching, temperature adjustments, and chat bubbles:

```bash
source .venv/bin/activate
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

### Step 6: Test Container Locally (Docker)

1. **Build the container image**:
   ```bash
   docker build -t gemini-langchain-chatbot:latest .
   ```

2. **Run the container locally** (mounting your local ADC credentials):
   ```bash
   docker run -p 8080:8080 \
     -e GOOGLE_CLOUD_PROJECT="your-gcp-project-id" \
     -v ~/.config/gcloud:/root/.config/gcloud \
     gemini-langchain-chatbot:latest
   ```

3. Open `http://localhost:8080` in your web browser.

---

### Step 7: Deploy to Google Cloud Run

Deploy directly from source to a serverless, auto-scaling HTTPS endpoint on Google Cloud:

```bash
gcloud run deploy gemini-chatbot \
  --source . \
  --region us-central1 \
  --set-env-vars GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID",GOOGLE_CLOUD_LOCATION="us-central1" \
  --allow-unauthenticated
```

Cloud Run will build the container using Cloud Build, deploy it to a dedicated endpoint, and output the live service URL.

---

## Advanced Extensions

1. **RAG (Retrieval-Augmented Generation)**:
   - Ground Gemini with enterprise documents by connecting **Vertex AI Search** or a Vector Store (e.g. `Cloud SQL for PostgreSQL with pgvector`).
2. **Tool / Function Calling**:
   - Equip Gemini with tools (`@tool` decorator in LangChain) to query BigQuery, make REST API calls, or run Python code.
3. **Persistent Session Memory**:
   - Replace `InMemoryChatMessageHistory` with **Google Cloud Firestore** (`FirestoreChatMessageHistory`) to persist conversations across user sessions and container restarts.
