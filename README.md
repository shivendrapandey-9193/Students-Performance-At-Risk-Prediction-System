# Student Insight AI — Full-Stack Academic Analytics & Early-Warning Platform

A full-stack AI-powered educational analytics and early-warning decision-support SaaS platform. 

Combines a **React.js** web application (Vite + Tailwind CSS), a **Node.js Express** API gateway, an integrated **Groq-powered conversational AI assistant** (`qwen/qwen3.8-27b`), and a **FastAPI** machine learning microservice hosting a calibrated **Random Forest Classifier** trained on the Open University Learning Analytics Dataset (OULAD).

---

## 1. System Architecture

```text
                                  +---------------------------+
                                  |   Web Browser / Client    |
                                  +-------------+-------------+
                                                |
                                                v
               +-----------------------------------------------------------------+
               |                  React.js Frontend SPA (Port 3000)              |
               |                                                                 |
               |  - Public SaaS Welcome / Landing Page ("/")                     |
               |  - Student Risk Analysis ("/app/student-analysis")              |
               |      * Individual Analysis Mode                                 |
               |      * Batch Student Screening Mode                             |
               |  - Model Insights & Explainability ("/app/model-insights")       |
               |  - Floating Project-Aware Insight AI Assistant                  |
               +--------------------------------+--------------------------------+
                                                |
                                                v  HTTP / JSON (/api/*)
               +--------------------------------+--------------------------------+
               |                  Node.js & Express Gateway (Port 5000)          |
               |                                                                 |
               |  - Multer CSV Upload & Stream Parsing                           |
               |  - Feature Sanitization & Monotonicity Validation               |
               |  - Embedded Project Domain Knowledge Base                       |
               |  - Groq Cloud LLM Integration (Qwen-2.5 32B / Llama 3)          |
               |  - Serving React Production Build (Single-Port Deployment)      |
               +---------------+--------------------------------+----------------+
                               |                                |
        Groq API / HTTPS       |                                | Internal HTTP Requests
        (LLM Assistant)        v                                v
+------------------------------+----+        +-----------------------------------+
|       Groq Cloud Platform         |        |   Python FastAPI Service          |
| (https://api.groq.com/openai/v1)  |        |   (Port 8000 / Render Cloud)      |
| Model: qwen/qwen3.8-27b           |        |   src/api/app.py                  |
+-----------------------------------+        +-----------------+-----------------+
                                                               |
                                                               v
                                             +-----------------------------------+
                                             |     Random Forest Pipeline        |
                                             |  - 100 Trees, Depth=10            |
                                             |  - Calibrated Cutoff = 0.24567    |
                                             |  - 12 Behavioral Click Features   |
                                             +-----------------------------------+
```

---

## 2. Key Pages & Workspaces

The platform provides two decoupled layouts:

1. **Public Welcome & Landing Page (`/`)**:
   - High-converting modern SaaS design inspired by Linear and Stripe.
   - Interactive live-like product preview.
   - 4 Feature pillars: 12 Behavioral Clickstream Features, Recall-Focused Decision Cutoff, Batch Cohort Triage, Insight AI Assistant.
   - 3-Step chronological workflow: Ingest clickstream, Compute calibrated inference, Deliver proactive interventions.
   - Full-stack technology stack breakdown and quick action launch buttons.
   - **Strictly preserves navigation: never auto-redirects to `/app`.**

2. **Main Application Workspace (`/app`)**:
   - `/app` directly redirects to `/app/student-analysis`.
   - **Student Risk Analysis (`/app/student-analysis`)**: Primary operational workspace with segmented toggle between:
     - *Individual Analysis*: Interactive 12-feature inputs, preset selector ("High Risk Student", "Borderline Student", "High Achieving Student"), animated probability gauge, risk classification badge, threshold comparison, and educator support suggestions.
     - *Batch Student Screening*: Drag-and-drop CSV upload, "Download Sample CSV" link, live file preview, batch prediction runner, cohort summary cards (total evaluated, at-risk count, not-at-risk count), risk distribution chart, searchable/sortable results table with individual record inspection, and CSV export.
   - **Model Insights (`/app/model-insights`)**: 5 compact, focused sections:
     1. Model Performance (Accuracy 74.32%, Recall 63.52%, Precision 9.08%, F1 15.89%, ROC-AUC 77.84%, PR-AUC 12.90%).
     2. Test Confusion Matrix (TN: 29,523, FP: 9,971, FN: 572, TP: 996).
     3. Feature Importance Attribution (12 features).
     4. Model Configuration & Methodology (OULAD, Random Forest, 0.2457 cutoff, chronological split).
     5. Responsible AI & Advisory Use (non-punitive decision support, demographic exclusion).

3. **Persistent Insight AI Assistant**:
   - Floating drawer available throughout the `/app` workspace.
   - Powered by Groq Cloud API (`qwen/qwen3.8-27b`) with complete conversational memory.
   - Embedded with full verified project facts, metrics, and interview preparation knowledge.
   - Quick suggested prompt chips ("Explain This Project", "Explain the ML Architecture", "What Challenges Did We Solve?", "Explain Model Performance", "Prepare Me for Interviews", "How Does Student Prediction Work?").

---

## 3. Verified Model Performance (2014J Test Cohort)

Evaluated strictly on the held-out chronological test cohort from presentation **2014J** (41,062 assessment records):

| Metric | Score | Operational Significance |
| :--- | :---: | :--- |
| **Accuracy** | **74.32%** | Balanced overall classification accuracy |
| **Recall (Sensitivity)** | **63.52%** | Intercepts 996 out of 1,568 students scoring below 40 |
| **Precision** | **9.08%** | Controlled trade-off on imbalanced class (3.82% base rate) |
| **F1 Score** | **15.89%** | Harmonic mean of precision and recall |
| **ROC-AUC** | **77.84%** | Strong discrimination capability across all thresholds |
| **PR-AUC** | **12.90%** | Evaluation baseline for extreme class imbalance |
| **Balanced Accuracy** | **69.14%** | Average of sensitivity and specificity |
| **Decision Cutoff** | **0.2457** | Validation-tuned threshold on 2014B cohort |

### Confusion Matrix (Test Split 2014J)
- **True Negatives (TN):** 29,523 (Passing students correctly identified)
- **False Positives (FP):** 9,971 (Passing students flagged for advisory check-in)
- **False Negatives (FN):** 572 (Missed failing students — minimized by design)
- **True Positives (TP):** 996 (Struggling students successfully caught in advance)

### Why 90% Accuracy Is Deceptive
In datasets with 3.8% positive cases:
- A naive dummy classifier predicting "safe" 100% of the time achieves **96.2% accuracy** with **0% recall**, detecting zero struggling students.
- LightGBM tuned for accuracy achieves **90.88% accuracy**, but recall collapses to **30.93%**, missing 1,083 out of 1,568 failing students.
- Our calibrated Random Forest deliberately prioritizes **63.52% recall** to maximize academic retention.

---

## 4. Local Execution & Startup Guide

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+ with `.venv`
- Groq API Key

### Step 1: Start the Python ML Microservice
```powershell
cd E:\Student-At-Risk-Prediction
.\.venv\Scripts\Activate.ps1
python -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```
*Health probe: `http://127.0.0.1:8000/health`*

### Step 2: Start the Node.js Express Gateway
```powershell
cd E:\Student-At-Risk-Prediction\backend
npm start
```
*Gateway running at `http://localhost:5000` (automatically proxies ML calls to local port 8000 with automatic fallback to Render cloud service).*

### Step 3: Start the React Frontend (Development)
```powershell
cd E:\Student-At-Risk-Prediction\frontend
npm run dev
```
*Web application opens at `http://localhost:3000`.*

---

## 5. Single-Port Production Deployment

The Node.js backend automatically serves the built React application from `frontend/dist` when present:

```powershell
# Build frontend
cd E:\Student-At-Risk-Prediction\frontend
npm run build

# Start production server
cd E:\Student-At-Risk-Prediction\backend
npm start
```
The entire application (Welcome page, Dashboard, Batch upload, and AI Assistant) is then accessible on a single port at `http://localhost:5000`.

---

## 6. Automated Testing

Run the test suite verifying all 26 unit tests across the ML model, API validation, and metrics integrity:
```powershell
cd E:\Student-At-Risk-Prediction
.\.venv\Scripts\python.exe -m pytest tests/
```
All 26 automated unit tests pass with 100% green coverage.
