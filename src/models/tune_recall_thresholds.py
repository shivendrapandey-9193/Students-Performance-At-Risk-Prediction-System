from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
)

ROOT = Path(__file__).resolve().parents[2]

VALIDATION = ROOT / "data/processed/validation.csv"
MODEL_DIR = ROOT / "models/candidates"
OUTPUT = ROOT / "reports/evaluation/recall_threshold_comparison.json"

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

df = pd.read_csv(VALIDATION)
X = df[features].copy()
y = df["target_low_score"].astype(int)

for col in categorical:
    X[col] = X[col].fillna("Unknown").astype(str)

models = [
    "random_forest",
    "lightgbm",
    "xgboost",
    "catboost",
]

results = []

for name in models:
    print(f"\nEvaluating {name} on validation data...")

    model = joblib.load(MODEL_DIR / f"{name}.joblib")
    probabilities = model.predict_proba(X)[:, 1]

    thresholds = np.unique(
        np.concatenate([
            np.linspace(0.01, 0.99, 500),
            [0.458283, 0.727802],
        ])
    )

    for target_recall in [0.60, 0.70]:
        valid_options = []

        for threshold in thresholds:
            predictions = (probabilities >= threshold).astype(int)

            precision = precision_score(
                y, predictions, zero_division=0
            )
            recall = recall_score(
                y, predictions, zero_division=0
            )
            f1 = f1_score(y, predictions, zero_division=0)

            if recall >= target_recall:
                valid_options.append({
                    "model": name,
                    "target_recall": target_recall,
                    "threshold": float(threshold),
                    "precision": float(precision),
                    "recall": float(recall),
                    "f1": float(f1),
                    "pr_auc": float(
                        average_precision_score(y, probabilities)
                    ),
                    "flagged_students": int(predictions.sum()),
                })

        if valid_options:
            best = max(
                valid_options,
                key=lambda item: (
                    item["precision"],
                    item["f1"],
                ),
            )
            results.append(best)
            print(best)
        else:
            print(f"No threshold achieved recall {target_recall:.0%}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as file:
    json.dump(results, file, indent=4)

print("\nResults saved:", OUTPUT)
print("\nValidation-only threshold optimization complete.")
