"""
Unit tests for the Random Forest machine learning pipeline and artifact.
Verifies model architecture, feature ordering, preprocessing pipelines,
probability computations, and reproducible inference.
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from src.dashboard.config import MODEL_METADATA, VERIFIED_METRICS

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "candidates" / "random_forest.joblib"


def test_model_artifact_loadable():
    """Verify that the saved model artifact loads as a valid scikit-learn Pipeline."""
    assert MODEL_PATH.exists(), f"Model artifact missing at {MODEL_PATH}"
    pipeline = joblib.load(MODEL_PATH)
    assert isinstance(pipeline, Pipeline)
    assert "preprocessor" in pipeline.named_steps
    assert "classifier" in pipeline.named_steps


def test_model_feature_names_order():
    """Verify that the model's feature names match expected 12 features in exact order."""
    pipeline = joblib.load(MODEL_PATH)
    expected_features = [
        "code_module",
        "code_presentation",
        "target_assessment_type",
        "target_date",
        "total_clicks",
        "activity_records",
        "active_days",
        "active_days_last_30_days",
        "clicks_last_7_days",
        "clicks_last_14_days",
        "clicks_last_30_days",
        "average_clicks_per_active_day",
    ]
    assert hasattr(pipeline, "feature_names_in_")
    assert pipeline.feature_names_in_.tolist() == expected_features


def test_model_reproducible_prediction_probability():
    """Verify that inference with standard sample input yields identical probability."""
    pipeline = joblib.load(MODEL_PATH)
    sample_df = pd.DataFrame([{
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
    }])

    proba = pipeline.predict_proba(sample_df)
    assert proba.shape == (1, 2)
    # Binary probabilities must sum to 1.0
    np.testing.assert_almost_equal(proba[0, 0] + proba[0, 1], 1.0)
    # Verified probability for this sample input is 0.0890 (8.90%)
    assert round(float(proba[0, 1]), 3) == 0.089


def test_classifier_hyperparameters_intact():
    """Verify that the classifier hyperparameters match the validated production configuration."""
    pipeline = joblib.load(MODEL_PATH)
    clf = pipeline.named_steps["classifier"]
    assert clf.n_estimators == 300
    assert clf.max_depth == 15
    assert clf.min_samples_leaf == 5
    assert clf.class_weight == "balanced_subsample"
    assert clf.random_state == 42


def test_threshold_comparison():
    """Verify threshold classification against production threshold."""
    threshold = MODEL_METADATA["threshold"]
    assert threshold == 0.24567134268537077

    # Probability below threshold -> Not flagged
    assert (0.089 >= threshold) is False

    # Probability above threshold -> Flagged
    assert (0.320 >= threshold) is True
