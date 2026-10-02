# 🏛️ AI-Powered Municipal Grievance Redressal & Intelligent Routing Portal

An end-to-end full-stack civic governance platform designed to automate citizen complaint classification, semantic deduplication, GIS hotspot analytics, and closed-loop field resolution verification.

## 🚀 Key Features
- **AI Triage & Dynamic Routing:** Multinomial ML classification for automated departmental tagging and SLA-based priority indexing.
- **Semantic Deduplication:** Uses sentence-transformers (`all-MiniLM-L6-v2`) to compute cosine similarity across active tickets.
- **Automated SOP Dispatch:** Real-time generation of crew allocation and equipment requirements for field teams.
- **Closed-Loop Citizen Verification:** Anti-"fake resolve" audit trail allowing citizens to verify ground reality.
- **GIS Hotspot Mapping:** Interactive OpenStreetMap integration visualizing incident clusters.

## 🛠️ Tech Stack
- **Frontend:** Streamlit, Plotly Express
- **Backend:** FastAPI, Uvicorn, SQLAlchemy (SQLite)
- **AI/ML:** Scikit-Learn, Sentence-Transformers, PyTorch, NumPy, Joblib

## ⚙️ How to Run Locally

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt