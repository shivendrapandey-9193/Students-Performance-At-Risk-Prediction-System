
from pathlib import Path
import json

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    confusion_matrix,
)

ROOT = Path(__file__).resolve().parents[2]

TRAIN_FILE = ROOT / "data" / "processed" / "train.csv"
VALIDATION_FILE = ROOT / "data" / "processed" / "validation.csv"

OUTPUT_DIR = ROOT / "reports" / "evaluation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "target_low_score"

# Load datasets
train = pd.read_csv(TRAIN_FILE)
validation = pd.read_csv(VALIDATION_FILE)

y_train = train[TARGET]
y_validation = validation[TARGET]

# Baseline: always predict the majority class
model = DummyClassifier(strategy="most_frequent")
model.fit(pd.DataFrame(index=range(len(y_train))), y_train)

predictions = model.predict(
    pd.DataFrame(index=range(len(y_validation)))
)

# Evaluate
metrics = {
    "model": "DummyClassifier (most_frequent)",
    "accuracy": accuracy_score(y_validation, predictions),
    "precision": precision_score(
        y_validation, predictions, zero_division=0
    ),
    "recall": recall_score(
        y_validation, predictions, zero_division=0
    ),
    "f1_score": f1_score(
        y_validation, predictions, zero_division=0
    ),
    "confusion_matrix": confusion_matrix(
        y_validation, predictions
    ).tolist(),
}

print("\nBASELINE MODEL RESULTS")
print("=" * 45)

for name, value in metrics.items():
    print(f"{name}: {value}")

# Save results
output_file = OUTPUT_DIR / "baseline_metrics.json"

with open(output_file, "w") as file:
    json.dump(metrics, file, indent=4)

print("\nResults saved to:", output_file)

