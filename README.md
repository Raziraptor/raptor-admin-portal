# 🦖 Raptor Admin Portal | AI-Powered Technical Ecosystem

**Raptor Admin Portal** is a production-grade **RAG (Retrieval-Augmented Generation)** platform designed for systems integrators and infrastructure engineers. It transforms static technical documentation (PDFs) into an interactive, context-aware knowledge base using State-of-the-Art Large Language Models.

---

## 🚀 The Mission
In high-stakes technical environments, finding specific data in 500-page manuals is a bottleneck. This portal automates information retrieval, allowing users to query infrastructure nuances, wiring diagrams, and configuration steps through a secure, conversational AI interface.

## 🛠️ Tech Stack
This project demonstrates a robust, containerized Full-Stack architecture:

* **Artificial Intelligence:** LangChain, Google Gemini Pro (LLM), Google Generative AI Embeddings.
* **Backend:** FastAPI (Python 3.12), SQLAlchemy ORM, JWT/OAuth2 Security.
* **Frontend:** React 18, Vite, Tailwind CSS, Lucide Icons.
* **Data Persistence:** * **PostgreSQL:** Relational data for users, roles, and metadata.
    * **ChromaDB:** High-performance Vector Database for document embeddings.
* **Infrastructure:** Docker & Docker Compose (Multi-container orchestration).

## ✨ Key Features
* **Intelligent RAG Pipeline:** Advanced document chunking and semantic search for high-precision technical answers.
* **Full CRUD Document Management:** Seamlessly upload, track, and manage technical manuals with real-time UI synchronization.
* **Enterprise-Ready Architecture:** Complete isolation of services (DB, API, Client) via Docker.
* **Secure Access:** Role-based access control and JWT-protected endpoints.
* **Source Traceability:** Every AI response includes references to the specific source documents for technical auditability.

---

## 📐 Architecture Overview
The system follows a modular micro-services approach:
1.  **Database (db):** A PostgreSQL instance managing structured data.
2.  **Backend (api):** A FastAPI orchestrator handling logic, AI chains, and vector processing.
3.  **Frontend (web):** A responsive React application serving a professional dashboard.

## ⚙️ Quick Start (Local Production)

The entire ecosystem is containerized for a **zero-configuration** experience.

### 1. Clone the repository
```bash
git clone [https://github.com/YourUsername/raptor-admin-portal.git](https://github.com/YourUsername/raptor-admin-portal.git)
cd raptor-admin-portal
