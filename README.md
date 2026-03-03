# ERP QA Assistant (RAG POC)

An intelligent, Retrieval-Augmented Generation (RAG) assistant designed to help employees navigate dense Enterprise Resource Planning (ERP) documentation. 

This Proof-of-Concept allows users to ask natural language questions and receive accurate, cited answers drawn directly from the provided manuals. It also features a dynamic document upload system, allowing evaluators or users to upload their own `.pdf` or `.txt` manuals and query them instantly!

## 🏗️ Architecture & Stack

The system is built as a lightweight, decoupled prototype focusing on speed, simplicity, and deployment readiness.

*   **Frontend:** React + Vite (Fast, reactive chat UI)
*   **Backend:** FastAPI + Uvicorn (High-performance async Python server)
*   **Orchestration:** LangChain (LCEL for document loading, splitting, and chaining)
*   **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (Runs 100% locally on CPU for high-speed, free semantic search)
*   **Vector Database:** FAISS (Local, in-memory vector store for blazing-fast retrieval without external DB dependencies)
*   **LLM Generator:** Google `gemini-flash-latest` (Extremely fast, reasoning-capable model accessed via a free-tier API)

### Why this architecture?
1.  **Deployment Friendly:** By offloading generative AI to the Gemini API, the backend can be hosted on standard, cheap infrastructure (e.g., Render, Railway) requiring only ~512MB RAM, without the need for expensive GPUs.
2.  **Performance:** The FAISS index is cached in memory on startup to prevent disk-read bottlenecks.
3.  **Accuracy & Edge Cases:** The system uses strict LangChain prompting to prevent hallucination (returning "Information not available" if the vector search yields no relevant context) and includes frontend/backend resilience for invalid queries.

---

## 🚀 How to Run Locally

### 1. Prerequisites
*   Node.js (v16+)
*   Python (**Recommended 3.11 or 3.12**. *Note: Python 3.13 on Windows may require C++/Rust build tools for some data science ML packages*.)

### 2. Backend Setup
Navigate to the backend directory and install the required packages:
```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory and add your Google Gemini API Key:
```env
GOOGLE_API_KEY="your_api_key_here"
```

Start the FastAPI server:
```bash
python main.py
```
*The server will run on `http://localhost:8000`.*

### 3. Frontend Setup
Open a new terminal, navigate to the frontend directory, and install dependencies:
```bash
cd frontend
npm install
```

Start the Vite development server:
```bash
npm run dev
```
*The React UI will run on `http://localhost:5173`.*

---

## 💡 Features
*   **Contextual QA:** Ask questions like *"How do I reverse a posted invoice?"*
*   **Source Citations:** Every answer cites the source document and page number it retrieved the information from.
*   **Dynamic Custom Uploads:** Click the 📁 icon next to the chat bar to upload your own `.pdf` or `.txt` file. The backend will instantly rebuild the FAISS vector index, and you can begin asking questions about your custom document immediately!
