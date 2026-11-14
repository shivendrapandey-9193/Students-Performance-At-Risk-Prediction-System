from pathlib import Path
import json
import joblib
import pandas as pd

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

DATA_DIR = ROOT / "data" / "processed"
MODEL_FILE = ROOT / "models" / "saved" / "random_forest.joblib"
OUTPUT_DIR = ROOT / "reports" / "evaluation"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "target_low_score"
THRESHOLD = 0.4583

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

model = joblib.load(MODEL_FILE)

datasets = {
    "seen_students": DATA_DIR / "test_seen_students.csv",
    "unseen_students": DATA_DIR / "test_unseen_students.csv",
}

results = {}

for name, file_path in datasets.items():
    data = pd.read_csv(file_path)

    X = data[features]
    y = data[TARGET]

    probabilities = model.predict_proba(X)[:, 1]
    predictions = (probabilities >= THRESHOLD).astype(int)

    metrics = {
        "records": int(len(data)),
        "unique_students": int(data["id_student"].nunique()),
        "at_risk_examples": int(y.sum()),
        "risk_rate": float(y.mean()),
        "accuracy": float(accuracy_score(y, predictions)),
        "precision": float(precision_score(y, predictions, zero_division=0)),
        "recall": float(recall_score(y, predictions, zero_division=0)),
        "f1_score": float(f1_score(y, predictions, zero_division=0)),
        "pr_auc": float(average_precision_score(y, probabilities)),
        "roc_auc": float(roc_auc_score(y, probabilities)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predictions)),
        "confusion_matrix": confusion_matrix(y, predictions).tolist(),
    }

    results[name] = metrics

    print("\n" + "=" * 50)
    print(name.upper())
    print("=" * 50)

    for key, value in metrics.items():
        print(f"{key}: {value}")

output_file = OUTPUT_DIR / "seen_unseen_evaluation.json"

with open(output_file, "w") as file:
    json.dump(results, file, indent=4)

print("\nEvaluation saved:", output_file)
