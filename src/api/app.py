"""
Student At-Risk Prediction API (FastAPI)
Advisory decision-support backend for upcoming student assessment screening.
Production-ready with CORS, structured schemas, batch inference, and Render deployment support.
"""

from pathlib import Path
import os
import logging
from typing import List, Optional
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
from src.api.chat import router as chat_router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("student-at-risk-api")

ROOT = Path(__file__).resolve().parents[2]

# Candidate paths for the trained model artifact
MODEL_CANDIDATES = [
    ROOT / "models" / "candidates" / "random_forest.joblib",
    ROOT / "models" / "saved" / "random_forest.joblib",
    ROOT / "artifacts" / "models" / "random_forest.joblib",
]

# Validation-tuned recall-focused decision threshold
THRESHOLD: float = 0.24567134268537077


def load_model_artifact():
    """Locate and load the trained Random Forest pipeline."""
    for path in MODEL_CANDIDATES:
        if path.exists():
            logger.info("Loading model artifact from %s", path)
            try:
                loaded = joblib.load(path)
                logger.info("Successfully loaded model artifact (%s)", type(loaded))
                return loaded, path
            except Exception as e:
                logger.error("Failed loading model from %s: %s", path, e)
    raise FileNotFoundError(
        f"Random Forest model artifact not found in any expected location: {[str(p) for p in MODEL_CANDIDATES]}"
    )


# Load model once at startup
try:
    model, MODEL_FILE = load_model_artifact()
except Exception as err:
    logger.critical("Model initialization failed: %s", err)
    model = None
    MODEL_FILE = MODEL_CANDIDATES[0]


app = FastAPI(
    title="Student Insight AI — At-Risk Prediction API",
    description=(
        "Advisory screening microservice predicting whether a student's next eligible "
        "TMA/CMA assessment score will fall below 40. Built with FastAPI and Scikit-Learn."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for local development and cloud deployments (e.g. Streamlit Cloud)
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Secure conversational endpoint; existing prediction routes remain unchanged.
app.include_router(chat_router)


# ---------------------------------------------------------------------------
# PYDANTIC SCHEMAS
# ---------------------------------------------------------------------------
class StudentFeatures(BaseModel):
    code_module: str = Field(..., description="Curriculum course module (AAA-GGG)")
    code_presentation: str = Field(..., description="Academic term presentation (e.g. 2014J)")
    target_assessment_type: str = Field(..., description="Tutor-Marked (TMA) or Computer-Marked (CMA)")

    target_date: float = Field(..., ge=0, description="Assessment due date relative to term start")
    total_clicks: float = Field(..., ge=0, description="Total cumulative clicks in VLE to date")
    activity_records: float = Field(..., ge=0, description="Total distinct activity interaction records")
    active_days: float = Field(..., ge=0, description="Total unique active calendar days")
    active_days_last_30_days: float = Field(..., ge=0, le=30, description="Active days in the last 30 days (max 30)")

    clicks_last_7_days: float = Field(..., ge=0, description="Clicks in the last 7 days")
    clicks_last_14_days: float = Field(..., ge=0, description="Clicks in the last 14 days")
    clicks_last_30_days: float = Field(..., ge=0, description="Clicks in the last 30 days")

    average_clicks_per_active_day: float = Field(..., ge=0, description="Average clicks per active study day")

    @model_validator(mode="after")
    def validate_activity(self):
        if not (
            self.clicks_last_7_days
            <= self.clicks_last_14_days
            <= self.clicks_last_30_days
            <= self.total_clicks
        ):
            raise ValueError("Click totals must satisfy logical monotonicity: 7d <= 14d <= 30d <= total")

        if self.active_days_last_30_days > self.active_days:
            raise ValueError("Recent active days (last 30) cannot exceed total active days")

        return self


class PredictionResponse(BaseModel):
    predicted_probability: float
    threshold: float
    flagged_for_review: bool
    risk_band: str
    decision_policy: str
    status: str
    message: str


class BatchPredictionRequest(BaseModel):
    students: List[StudentFeatures]


class BatchPredictionResponse(BaseModel):
    total_processed: int
    flagged_count: int
    safe_count: int
    threshold: float
    predictions: List[PredictionResponse]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model: str
    threshold: float
    version: str


# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------
@app.get("/", summary="API Root & Metadata")
def home():
    """Returns platform metadata, active model name, and policy."""
    return {
        "message": "Student Insight AI — At-Risk Prediction API is running",
        "model": "Random Forest - Recall Focused",
        "threshold": THRESHOLD,
        "model_file": str(MODEL_FILE.name) if MODEL_FILE else "unavailable",
        "decision_policy": "Recall-focused; human review required",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, summary="Service Health Probe")
def health():
    """Live health probe verifying model availability and configuration."""
    return HealthResponse(
        status="healthy" if model is not None else "degraded",
        model_loaded=model is not None,
        model="Random Forest - Recall Focused",
        threshold=THRESHOLD,
        version="1.0.0",
    )


@app.post("/predict", response_model=PredictionResponse, summary="Individual Student Risk Prediction")
def predict_student(features: StudentFeatures):
    """
    Score a single student's pre-assessment engagement profile.
    Returns predicted probability of score < 40 and review recommendation.
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded on this server.",
        )

    try:
        input_data = pd.DataFrame([features.model_dump()])
        probability = float(model.predict_proba(input_data)[0, 1])
        flagged = probability >= THRESHOLD

        return PredictionResponse(
            predicted_probability=round(probability, 4),
            threshold=THRESHOLD,
            flagged_for_review=flagged,
            risk_band="Review recommended" if flagged else "Below review threshold",
            decision_policy="Recall-focused threshold selected on validation data",
            status="Review recommended" if flagged else "Not flagged by this model",
            message=(
                "This is an advisory prediction, not a confirmed outcome. "
                "A qualified educator must review the student's circumstances."
            ),
        )

    except Exception as error:
        logger.error("Single prediction failed: %s", error, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(error)}",
        )


@app.post("/predict/batch", response_model=BatchPredictionResponse, summary="Batch Student Cohort Risk Prediction")
def predict_batch(batch: BatchPredictionRequest):
    """
    Score an entire cohort of student records in a single vectorized inference pass.
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded on this server.",
        )

    if not batch.students:
        return BatchPredictionResponse(
            total_processed=0,
            flagged_count=0,
            safe_count=0,
            threshold=THRESHOLD,
            predictions=[],
        )

    try:
        records = [s.model_dump() for s in batch.students]
        input_data = pd.DataFrame(records)
        probabilities = model.predict_proba(input_data)[:, 1]

        predictions: List[PredictionResponse] = []
        flagged_count = 0

        for prob_raw in probabilities:
            prob = float(prob_raw)
            flagged = prob >= THRESHOLD
            if flagged:
                flagged_count += 1

            predictions.append(
                PredictionResponse(
                    predicted_probability=round(prob, 4),
                    threshold=THRESHOLD,
                    flagged_for_review=flagged,
                    risk_band="Review recommended" if flagged else "Below review threshold",
                    decision_policy="Recall-focused threshold selected on validation data",
                    status="Review recommended" if flagged else "Not flagged by this model",
                    message=(
                        "This is an advisory prediction, not a confirmed outcome. "
                        "A qualified educator must review the student's circumstances."
                    ),
                )
            )

        return BatchPredictionResponse(
            total_processed=len(predictions),
            flagged_count=flagged_count,
            safe_count=len(predictions) - flagged_count,
            threshold=THRESHOLD,
            predictions=predictions,
        )

    except Exception as error:
        logger.error("Batch prediction failed: %s", error, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(error)}",
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    logger.info("Starting Uvicorn server on %s:%d", host, port)
    uvicorn.run("src.api.app:app", host=host, port=port, reload=False)
