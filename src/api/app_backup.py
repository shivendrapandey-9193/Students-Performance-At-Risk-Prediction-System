from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator

ROOT = Path(__file__).resolve().parents[2]

MODEL_FILE = ROOT / "models" / "saved" / "random_forest.joblib"

THRESHOLD = 0.4583

app = FastAPI(
    title="Student At-Risk Prediction API",
    description="Advisory predictions for upcoming student assessments.",
    version="1.0.0",
)

# Load trained model once when the API starts
model = joblib.load(MODEL_FILE)


class StudentFeatures(BaseModel):
    code_module: str
    code_presentation: str
    target_assessment_type: str

    target_date: float = Field(ge=0)
    total_clicks: float = Field(ge=0)
    activity_records: float = Field(ge=0)
    active_days: float = Field(ge=0)
    active_days_last_30_days: float = Field(ge=0, le=30)

    clicks_last_7_days: float = Field(ge=0)
    clicks_last_14_days: float = Field(ge=0)
    clicks_last_30_days: float = Field(ge=0)

    average_clicks_per_active_day: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_activity(self):
        if not (
            self.clicks_last_7_days
            <= self.clicks_last_14_days
            <= self.clicks_last_30_days
            <= self.total_clicks
        ):
            raise ValueError("Click totals must follow 7d <= 14d <= 30d <= total")

        if self.active_days_last_30_days > self.active_days:
            raise ValueError("Recent active days cannot exceed total active days")

        return self


@app.get("/")
def home():
    return {
        "message": "Student At-Risk Prediction API is running",
        "model": "Random Forest - Conservative",
        "threshold": THRESHOLD,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }


@app.post("/predict")
def predict_student(features: StudentFeatures):
    try:
        input_data = pd.DataFrame([features.model_dump()])

        probability = float(model.predict_proba(input_data)[0, 1])

        flagged = probability >= THRESHOLD

        return {
            "predicted_probability": round(probability, 4),
            "threshold": THRESHOLD,
            "flagged_for_review": flagged,
            "status": (
                "Review recommended"
                if flagged
                else "Not flagged by this model"
            ),
            "message": (
                "This is an advisory prediction, not a confirmed outcome. "
                "A qualified educator must review the student's circumstances."
            ),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}",
        )
