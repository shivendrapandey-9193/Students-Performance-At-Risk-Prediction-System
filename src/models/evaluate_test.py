
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

TEST_FILE = ROOT / "data" / "processed" / "test.csv"
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

# Load untouched test data and selected model
test = pd.read_csv(TEST_FILE)
model = joblib.load(MODEL_FILE)

X_test = test[features]
y_test = test[TARGET]

print("Evaluating Random Forest on final test data...")

# Generate probabilities and apply validation-selected threshold
probabilities = model.predict_proba(X_test)[:, 1]
predictions = (probabilities >= THRESHOLD).astype(int)

# Calculate final metrics
metrics = {
    "model": "Random Forest - Conservative",
    "threshold": THRESHOLD,
    "test_records": int(len(test)),
    "accuracy": float(accuracy_score(y_test, predictions)),
    "precision": float(precision_score(y_test, predictions, zero_division=0)),
    "recall": float(recall_score(y_test, predictions, zero_division=0)),
    "f1_score": float(f1_score(y_test, predictions, zero_division=0)),
    "pr_auc": float(average_precision_score(y_test, probabilities)),
    "roc_auc": float(roc_auc_score(y_test, probabilities)),
    "balanced_accuracy": float(balanced_accuracy_score(y_test, predictions)),
    "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
}

print("\nFINAL TEST RESULTS")
print("=" * 45)

for name, value in metrics.items():
    print(f"{name}: {value}")

# Save final evaluation
output_file = OUTPUT_DIR / "final_test_metrics.json"

with open(output_file, "w") as file:
    json.dump(metrics, file, indent=4)

print("\nFinal results saved:", output_file)
