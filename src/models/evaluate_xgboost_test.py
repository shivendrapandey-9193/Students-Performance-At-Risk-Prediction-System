from pathlib import Path
import json
import time

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[2]

TEST_PATH = ROOT / "data" / "processed" / "test.csv"
MODEL_PATH = ROOT / "models" / "candidates" / "xgboost.joblib"
THRESHOLD_PATH = ROOT / "reports" / "evaluation" / "candidate_thresholds.json"
OUTPUT_PATH = ROOT / "reports" / "evaluation" / "xgboost_final_test_metrics.json"

TARGET = "target_low_score"

FEATURES = [
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

CATEGORICAL = [
    "code_module",
    "code_presentation",
    "target_assessment_type",
]

print("Loading XGBoost model...")
model = joblib.load(MODEL_PATH)

with open(THRESHOLD_PATH, "r", encoding="utf-8") as file:
    threshold = float(json.load(file)["xgboost"]["threshold"])

print("Loading final test dataset...")
test_df = pd.read_csv(TEST_PATH)

X_test = test_df[FEATURES].copy()
y_test = test_df[TARGET].astype(int)

for column in CATEGORICAL:
    X_test[column] = X_test[column].fillna("Unknown").astype(str)

print(f"Test rows: {len(X_test):,}")
print(f"Positive cases: {int(y_test.sum()):,}")
print(f"Threshold: {threshold:.6f}")

print("Running final evaluation...")
start = time.perf_counter()
probabilities = model.predict_proba(X_test)[:, 1]
inference_seconds = time.perf_counter() - start

predictions = (probabilities >= threshold).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_test, predictions, labels=[0, 1]
).ravel()

metrics = {
    "model": "XGBoost",
    "threshold": threshold,
    "test_rows": int(len(y_test)),
    "positive_cases": int(y_test.sum()),
    "accuracy": float(accuracy_score(y_test, predictions)),
    "precision": float(precision_score(y_test, predictions, zero_division=0)),
    "recall": float(recall_score(y_test, predictions, zero_division=0)),
    "f1": float(f1_score(y_test, predictions, zero_division=0)),
    "pr_auc": float(average_precision_score(y_test, probabilities)),
    "roc_auc": float(roc_auc_score(y_test, probabilities)),
    "balanced_accuracy": float(balanced_accuracy_score(y_test, predictions)),
    "true_negatives": int(tn),
    "false_positives": int(fp),
    "false_negatives": int(fn),
    "true_positives": int(tp),
    "inference_seconds": float(inference_seconds),
    "rows_per_second": float(len(X_test) / inference_seconds),
}

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
    json.dump(metrics, file, indent=4)

print("\n" + "=" * 55)
print("XGBOOST FINAL TEST RESULTS")
print("=" * 55)

for key, value in metrics.items():
    print(f"{key}: {value:.4f}" if isinstance(value, float) else f"{key}: {value}")

print("\nSaved:", OUTPUT_PATH)
print("Threshold was selected using validation data only.")
