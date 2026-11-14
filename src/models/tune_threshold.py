
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    precision_recall_curve,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

ROOT = Path(__file__).resolve().parents[2]

VALIDATION_FILE = ROOT / "data" / "processed" / "validation.csv"
MODEL_DIR = ROOT / "models" / "saved"
REPORT_DIR = ROOT / "reports" / "evaluation"

TARGET = "target_low_score"

categorical_features = [
    "code_module",
    "code_presentation",
    "target_assessment_type",
]

numeric_features = [
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

features = categorical_features + numeric_features

validation = pd.read_csv(VALIDATION_FILE)
X_validation = validation[features]
y_validation = validation[TARGET]

models = {
    "Logistic Regression": MODEL_DIR / "logistic_regression.joblib",
    "Random Forest": MODEL_DIR / "random_forest.joblib",
}

all_results = {}
comparison_rows = []

for model_name, model_path in models.items():
    print(f"\nAnalyzing {model_name}...")

    model = joblib.load(model_path)
    probabilities = model.predict_proba(X_validation)[:, 1]

    precision, recall, thresholds = precision_recall_curve(
        y_validation, probabilities
    )

    # F1 for each available threshold
    f1_values = (
        2 * precision[:-1] * recall[:-1]
        / (precision[:-1] + recall[:-1] + 1e-12)
    )

    best_index = int(np.argmax(f1_values))
    best_threshold = float(thresholds[best_index])

    # Find best precision among thresholds with recall >= 60%
    eligible = np.where(recall[:-1] >= 0.60)[0]

    if len(eligible) > 0:
        recall_index = eligible[
            np.argmax(precision[:-1][eligible])
        ]
        recall_threshold = float(thresholds[recall_index])
        recall_precision = float(precision[recall_index])
        achieved_recall = float(recall[recall_index])
    else:
        recall_threshold = None
        recall_precision = None
        achieved_recall = None

    predictions = (probabilities >= best_threshold).astype(int)

    result = {
        "model": model_name,
        "best_f1_threshold": best_threshold,
        "best_f1": float(f1_values[best_index]),
        "precision_at_best_f1": float(
            precision_score(y_validation, predictions, zero_division=0)
        ),
        "recall_at_best_f1": float(
            recall_score(y_validation, predictions, zero_division=0)
        ),
        "confusion_matrix_at_best_f1": confusion_matrix(
            y_validation, predictions
        ).tolist(),
        "threshold_for_recall_at_least_60_percent": recall_threshold,
        "precision_at_that_threshold": recall_precision,
        "achieved_recall": achieved_recall,
    }

    all_results[model_name] = result

    comparison_rows.append({
        "model": model_name,
        "best_threshold": best_threshold,
        "best_f1": result["best_f1"],
        "precision": result["precision_at_best_f1"],
        "recall": result["recall_at_best_f1"],
    })

    print("Best threshold:", round(best_threshold, 4))
    print("Best F1:", round(result["best_f1"], 4))
    print("Precision:", round(result["precision_at_best_f1"], 4))
    print("Recall:", round(result["recall_at_best_f1"], 4))
    print("Confusion matrix:", result["confusion_matrix_at_best_f1"])

    print("\nBest precision with recall >= 60%:")
    print("Threshold:", recall_threshold)
    print("Precision:", recall_precision)
    print("Recall:", achieved_recall)

# Save results
REPORT_DIR.mkdir(parents=True, exist_ok=True)

json_path = REPORT_DIR / "threshold_tuning_results.json"

with open(json_path, "w") as file:
    json.dump(all_results, file, indent=4)

csv_path = REPORT_DIR / "threshold_comparison.csv"

pd.DataFrame(comparison_rows).to_csv(csv_path, index=False)

print("\nTHRESHOLD TUNING COMPLETED")
print("JSON:", json_path)
print("CSV:", csv_path)
