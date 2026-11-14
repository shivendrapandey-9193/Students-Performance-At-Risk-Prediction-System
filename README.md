# Student Insight AI — Academic Performance & At-Risk Prediction System

An enterprise-grade educational analytics and early-alert decision-support platform. Built with a verified **Random Forest Classifier**, a **FastAPI** inference backend, and an interactive **Streamlit** dashboard.

---

## 1. System Architecture

```text
                           +------------------------+
                           |   GitHub Repository    |
                           +-----------+------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
      +------------------------+              +------------------------+
      | Streamlit Cloud / Web  |              |  Render Web Service    |
      | (Frontend Dashboard)   |              |  (FastAPI Backend)     |
      |   src/dashboard/app.py |              |   src/api/app.py       |
      +-----------+------------+              +-----------+------------+
                  |                                       |
                  |         HTTPS REST Requests           |
                  +-------------------------------------> |
                  |                                       v
                  |                           +------------------------+
                  |                           | Random Forest Pipeline |
                  |                           | (models/candidates/..) |
                  |                           +------------------------+
                  |                                       |
                  | <-------------------------------------+
                  |           JSON Risk Assessment
                  v
       Educator Decision Support
```

The frontend and backend are completely decoupled and independently deployable:
- **Backend:** Serves REST API endpoints (`/health`, `/predict`, `/predict/batch`) via FastAPI and Uvicorn.
- **Frontend:** Streamlit SaaS application that consumes the backend API and provides interactive visualizations.
- **Model:** Pre-trained Random Forest pipeline with validation-tuned threshold ($\tau = 0.24567$) prioritizing recall.

---

## 2. Verified Model Performance

Evaluated strictly on the held-out chronological test cohort from presentation **2014J** (41,062 assessment records):

| Metric | Score | Operational Significance |
| :--- | :---: | :--- |
| **Accuracy** | **74.32%** | Overall correct classifications across all test records |
| **Recall (Sensitivity)** | **63.52%** | Intercepts ~64% of all students scoring below 40 |
| **Precision** | **9.08%** | Controlled trade-off on imbalanced class (3.82% base rate) |
| **F1 Score** | **15.89%** | Harmonic mean of precision and recall |
| **ROC-AUC** | **77.84%** | Strong discrimination capability across all thresholds |
| **PR-AUC** | **12.90%** | Evaluation baseline for extreme class imbalance |
| **Balanced Accuracy** | **69.14%** | Average of sensitivity and specificity |

### Confusion Matrix (Test Split 2014J)
- **True Negatives (TN):** 29,523
- **False Positives (FP):** 9,971 (Advisory alerts requiring educator triage)
- **False Negatives (FN):** 572
- **True Positives (TP):** 996 (Struggling students successfully identified)

---

## 3. Local Development Setup

### Prerequisites
- Python 3.11+
- Virtual environment tool (`venv`)

### Installation
Clone the repository and install dependencies:
```bash
git clone <your-repository-url>
cd Student-At-Risk-Prediction
python -m venv .venv
# On Windows:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### Running the Services

**Terminal 1 — Start the FastAPI Backend:**
```bash
python -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```
*API documentation available at `http://127.0.0.1:8000/docs`.*

**Terminal 2 — Start the Streamlit Frontend:**
```bash
streamlit run src/dashboard/app.py
```
*Dashboard opens at `http://localhost:8501`.*

---

## 4. Cloud Deployment Guide

### A. Deploy FastAPI Backend on Render
1. Push your repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com/), select **New > Web Service**.
3. Connect your repository.
4. Set the following configuration:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
5. Click **Create Web Service** and copy your live URL (e.g., `https://student-insight-api.onrender.com`).

*(Alternatively, use the included `render.yaml` for automatic Blueprint deployment).*

### B. Deploy Streamlit Dashboard on Streamlit Community Cloud
1. In the [Streamlit Community Cloud](https://share.streamlit.io/), create a new application pointing to your GitHub repo.
2. Set **Main file path:** `src/dashboard/app.py`.
3. In **Advanced Settings > Secrets**, configure the backend URL:
   ```toml
   API_BASE_URL = "https://your-render-service.onrender.com"
   ```
4. Click **Deploy**. The frontend will automatically route requests to the live backend.

---

## 5. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API status, active model variant, and policy description |
| `GET` | `/health` | Microservice health check probe and model loading verification |
| `POST` | `/predict` | Single student risk scoring |
| `POST` | `/predict/batch` | High-throughput vectorized batch scoring for cohorts |

---

## 6. Automated Testing

Run the full pytest suite (26 automated unit tests):
```bash
python -m pytest tests/ -v
```

Tests cover:
- Microservice health and prediction endpoints (`tests/test_api.py`)
- Machine learning pipeline, feature order, and reproducibility (`tests/test_model.py`)
- Dashboard metric integrity, chart generation, presets, and validation (`tests/test_dashboard.py`)

---

## 7. Ethical Governance Statement

> **Notice:** This platform is designed solely to assist educators in providing supportive, proactive academic guidance to students who may benefit from timely assistance. It is strictly prohibited from being utilized for automated grading, disciplinary actions, enrollment cancellation, or exclusion decisions. All model recommendations require qualified educator review.
