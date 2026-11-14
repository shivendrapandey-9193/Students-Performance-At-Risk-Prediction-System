from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

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

TRAIN_FILE = ROOT / "data" / "processed" / "train.csv"
VALIDATION_FILE = ROOT / "data" / "processed" / "validation.csv"

MODEL_DIR = ROOT / "models" / "saved"
REPORT_DIR = ROOT / "reports" / "evaluation"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "target_low_score"

# Load data
train = pd.read_csv(TRAIN_FILE)
validation = pd.read_csv(VALIDATION_FILE)

# Conservative feature configuration
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

X_train = train[features]
y_train = train[TARGET]

X_validation = validation[features]
y_validation = validation[TARGET]

# Preprocessing for categorical columns
categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore")),
])

# Preprocessing for numerical columns
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

preprocessor = ColumnTransformer([
    ("categorical", categorical_pipeline, categorical_features),
    ("numeric", numeric_pipeline, numeric_features),
])

# Complete ML pipeline
model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=42,
    )),
])

# Train
print("Training Logistic Regression...")
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_validation)
probabilities = model.predict_proba(X_validation)[:, 1]

# Evaluate
metrics = {
    "model": "Logistic Regression - Conservative",
    "accuracy": float(accuracy_score(y_validation, predictions)),
    "precision": float(precision_score(y_validation, predictions, zero_division=0)),
    "recall": float(recall_score(y_validation, predictions, zero_division=0)),
    "f1_score": float(f1_score(y_validation, predictions, zero_division=0)),
    "pr_auc": float(average_precision_score(y_validation, probabilities)),
    "roc_auc": float(roc_auc_score(y_validation, probabilities)),
    "balanced_accuracy": float(balanced_accuracy_score(y_validation, predictions)),
    "confusion_matrix": confusion_matrix(
        y_validation, predictions
    ).tolist(),
}

print("\nLOGISTIC REGRESSION RESULTS")
print("=" * 45)

for name, value in metrics.items():
    print(f"{name}: {value}")

# Save trained pipeline
model_path = MODEL_DIR / "logistic_regression.joblib"
joblib.dump(model, model_path)

# Save metrics
metrics_path = REPORT_DIR / "logistic_regression_metrics.json"

with open(metrics_path, "w") as file:
    json.dump(metrics, file, indent=4)

print("\nModel saved:", model_path)
print("Metrics saved:", metrics_path)
