"""
Tests for the Student Insight AI FastAPI microservice.
Tests endpoints, schemas, validation rules, batch processing, and error handling.
"""

from pathlib import Path
import pytest
from pydantic import ValidationError

from src.api.app import (
    app,
    model,
    MODEL_FILE,
    THRESHOLD,
    home,
    health,
    predict_student,
    predict_batch,
    StudentFeatures,
    BatchPredictionRequest,
)

SAMPLE_INPUT = {
    "code_module": "AAA",
    "code_presentation": "2013B",
    "target_assessment_type": "TMA",
    "target_date": 30.0,
    "total_clicks": 1000.0,
    "activity_records": 300.0,
    "active_days": 40.0,
    "active_days_last_30_days": 10.0,
    "clicks_last_7_days": 100.0,
    "clicks_last_14_days": 250.0,
    "clicks_last_30_days": 500.0,
    "average_clicks_per_active_day": 25.0,
}


def test_model_artifact_exists():
    assert MODEL_FILE is not None
    assert MODEL_FILE.exists()
    assert "random_forest.joblib" in MODEL_FILE.name


def test_model_is_loaded():
    assert model is not None
    assert hasattr(model, "predict_proba")


def test_home_endpoint():
    data = home()
    assert data["model"] == "Random Forest - Recall Focused"
    assert data["threshold"] == THRESHOLD
    assert "random_forest.joblib" in data["model_file"]
    assert "version" in data


def test_health_endpoint():
    data = health()
    assert data.status == "healthy"
    assert data.model_loaded is True
    assert data.threshold == THRESHOLD
    assert data.version == "1.0.0"


def test_prediction_endpoint_valid_student():
    student = StudentFeatures(**SAMPLE_INPUT)
    res = predict_student(student)

    assert 0.0 <= res.predicted_probability <= 1.0
    assert res.threshold == THRESHOLD
    assert isinstance(res.flagged_for_review, bool)
    assert res.risk_band in ["Review recommended", "Below review threshold"]
    assert "advisory prediction" in res.message.lower()
    assert "qualified educator" in res.message.lower()


def test_prediction_decision_matches_threshold():
    student = StudentFeatures(**SAMPLE_INPUT)
    res = predict_student(student)

    expected_flag = res.predicted_probability >= THRESHOLD
    assert res.flagged_for_review == expected_flag


def test_batch_prediction_endpoint():
    s1 = StudentFeatures(**SAMPLE_INPUT)
    s2 = StudentFeatures(
        code_module="CCC",
        code_presentation="2014J",
        target_assessment_type="TMA",
        target_date=65.0,
        total_clicks=180.0,
        activity_records=42.0,
        active_days=12.0,
        active_days_last_30_days=3.0,
        clicks_last_7_days=0.0,
        clicks_last_14_days=15.0,
        clicks_last_30_days=45.0,
        average_clicks_per_active_day=15.0,
    )

    batch_req = BatchPredictionRequest(students=[s1, s2])
    res = predict_batch(batch_req)

    assert res.total_processed == 2
    assert len(res.predictions) == 2
    assert res.flagged_count + res.safe_count == 2
    assert res.threshold == THRESHOLD


def test_empty_batch_handled_cleanly():
    batch_req = BatchPredictionRequest(students=[])
    res = predict_batch(batch_req)
    assert res.total_processed == 0
    assert len(res.predictions) == 0


def test_invalid_click_sequence_is_rejected():
    invalid_input = SAMPLE_INPUT.copy()
    invalid_input["clicks_last_7_days"] = 300.0
    invalid_input["clicks_last_14_days"] = 200.0

    with pytest.raises(ValidationError) as exc:
        StudentFeatures(**invalid_input)
    assert "logical monotonicity" in str(exc.value)


def test_recent_active_days_cannot_exceed_total():
    invalid_input = SAMPLE_INPUT.copy()
    invalid_input["active_days"] = 5.0
    invalid_input["active_days_last_30_days"] = 10.0

    with pytest.raises(ValidationError) as exc:
        StudentFeatures(**invalid_input)
    assert "cannot exceed total active days" in str(exc.value)


def test_negative_clicks_are_rejected():
    invalid_input = SAMPLE_INPUT.copy()
    invalid_input["total_clicks"] = -100.0

    with pytest.raises(ValidationError):
        StudentFeatures(**invalid_input)


def test_missing_required_feature_is_rejected():
    invalid_input = SAMPLE_INPUT.copy()
    del invalid_input["total_clicks"]

    with pytest.raises(ValidationError):
        StudentFeatures(**invalid_input)
