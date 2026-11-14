from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    roc_auc_score,
    balanced_accuracy_score,
    confusion_matrix,
)

ROOT = Path(__file__).resolve().parents[2]

TEST_PATH = ROOT / "data/processed/test.csv"
MODEL_PATH = ROOT / "models/candidates/random_forest.joblib"
OUTPUT_PATH = (
    ROOT / "reports/evaluation/"
    "random_forest_recall60_test_metrics.json"
)

THRESHOLD = 0.24567134268537077

features = [
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

categorical = [
    "code_module",
    "code_presentation",
    "target_assessment_type",
]

df = pd.read_csv(TEST_PATH)
X = df[features].copy()
y = df["target_low_score"].astype(int)

for col in categorical:
    X[col] = X[col].fillna("Unknown").astype(str)

model = joblib.load(MODEL_PATH)

probabilities = model.predict_proba(X)[:, 1]
predictions = (probabilities >= THRESHOLD).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y, predictions, labels=[0, 1]
).ravel()

metrics = {
    "model": "random_forest",
    "dataset": "2014J_chronological_test",
    "threshold": THRESHOLD,
    "threshold_selected_on": "validation",
    "test_rows": int(len(y)),
    "actual_positive_cases": int(y.sum()),
    "flagged_students": int(predictions.sum()),
    "accuracy": float(accuracy_score(y, predictions)),
    "precision": float(precision_score(y, predictions, zero_division=0)),
    "recall": float(recall_score(y, predictions, zero_division=0)),
    "f1": float(f1_score(y, predictions, zero_division=0)),
    "pr_auc": float(average_precision_score(y, probabilities)),
    "roc_auc": float(roc_auc_score(y, probabilities)),
    "balanced_accuracy": float(balanced_accuracy_score(y, predictions)),
    "confusion_matrix": {
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
    },
}

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=4)

print(json.dumps(metrics, indent=4))
print("\nSaved:", OUTPUT_PATH)
