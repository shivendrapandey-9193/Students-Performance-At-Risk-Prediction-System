"""
Unit tests for the redesigned Student Insight AI Dashboard components,
configuration integrity, and validation logic.
"""

import pandas as pd
import pytest

from src.dashboard.config import (
    COLORS,
    MODEL_METADATA,
    VERIFIED_METRICS,
    CONFUSION_MATRIX,
    FEATURE_IMPORTANCE_DATA,
    BENCHMARK_MODELS,
    STUDENT_PRESETS,
    SAMPLE_BATCH_RECORDS,
)
from src.dashboard.api_client import (
    validate_batch_dataframe,
    REQUIRED_BATCH_COLUMNS,
    check_api_health,
)
from src.dashboard.ui_components import (
    render_confusion_matrix_chart,
    render_feature_importance_chart,
    render_benchmark_chart,
    render_probability_gauge,
)


def test_verified_evaluation_metrics_integrity():
    """Verify that verified metrics exactly match the held-out test evaluation report."""
    assert VERIFIED_METRICS["accuracy_display"] == "74.32%"
    assert VERIFIED_METRICS["precision_display"] == "9.08%"
    assert VERIFIED_METRICS["recall_display"] == "63.52%"
    assert VERIFIED_METRICS["f1_display"] == "15.89%"
    assert VERIFIED_METRICS["pr_auc_display"] == "12.90%"
    assert VERIFIED_METRICS["roc_auc_display"] == "77.84%"
    assert VERIFIED_METRICS["balanced_accuracy_display"] == "69.14%"


def test_confusion_matrix_counts():
    """Verify that confusion matrix counts match held-out test evaluation report."""
    assert CONFUSION_MATRIX["true_negatives"] == 29523
    assert CONFUSION_MATRIX["false_positives"] == 9971
    assert CONFUSION_MATRIX["false_negatives"] == 572
    assert CONFUSION_MATRIX["true_positives"] == 996

    total = sum(CONFUSION_MATRIX.values())
    assert total == 41062


def test_model_metadata_threshold():
    """Verify that decision threshold matches the validation-tuned threshold."""
    assert MODEL_METADATA["threshold"] == 0.24567134268537077
    assert MODEL_METADATA["threshold_display"] == "24.57%"


def test_feature_importance_list():
    """Verify that all 12 model features are represented in feature importance."""
    assert len(FEATURE_IMPORTANCE_DATA) == 12
    feature_names = [f["feature"] for f in FEATURE_IMPORTANCE_DATA]
    assert "code_module" in feature_names
    assert "active_days_last_30_days" in feature_names
    assert "clicks_last_30_days" in feature_names
    assert "code_module" == FEATURE_IMPORTANCE_DATA[0]["feature"]  # top feature


def test_student_presets_validity():
    """Verify all student preset profiles satisfy logical monotonicity."""
    for name, p in STUDENT_PRESETS.items():
        assert p["clicks_last_7_days"] <= p["clicks_last_14_days"], f"Preset {name} 7d > 14d"
        assert p["clicks_last_14_days"] <= p["clicks_last_30_days"], f"Preset {name} 14d > 30d"
        assert p["clicks_last_30_days"] <= p["total_clicks"], f"Preset {name} 30d > total"
        assert p["active_days_last_30_days"] <= p["active_days"], f"Preset {name} active 30d > total"


def test_batch_validation_valid():
    """Verify batch validation accepts well-formed data."""
    df = pd.DataFrame(SAMPLE_BATCH_RECORDS)
    valid, err, clean = validate_batch_dataframe(df)
    assert valid is True
    assert err is None
    assert len(clean) == len(SAMPLE_BATCH_RECORDS)
    for col in REQUIRED_BATCH_COLUMNS:
        assert col in clean.columns


def test_batch_validation_missing_columns():
    """Verify batch validation rejects DataFrame with missing columns."""
    df = pd.DataFrame([{"code_module": "AAA"}])
    valid, err, clean = validate_batch_dataframe(df)
    assert valid is False
    assert "Missing required columns" in err


def test_plotly_chart_generation():
    """Verify that all Plotly figures render properly without exceptions."""
    fig_cm = render_confusion_matrix_chart()
    assert fig_cm is not None
    assert len(fig_cm.data) == 1

    fig_fi = render_feature_importance_chart(FEATURE_IMPORTANCE_DATA)
    assert fig_fi is not None
    assert len(fig_fi.data) == 1

    fig_bm = render_benchmark_chart(BENCHMARK_MODELS)
    assert fig_bm is not None
    assert len(fig_bm.data) == 4

    fig_gauge = render_probability_gauge(0.35, 0.2457)
    assert fig_gauge is not None
    assert len(fig_gauge.data) == 2


def test_api_health_offline_handling():
    """Verify health check gracefully handles offline state without crashing."""
    res = check_api_health("http://127.0.0.1:9999", timeout=0.5)
    assert res["connected"] is False
    assert res["status"] in ["offline", "error", "timeout"]
