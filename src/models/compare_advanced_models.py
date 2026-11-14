
from pathlib import Path
import json
import time

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier


# --------------------------------------------------
# 1. Paths and reproducibility
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

TRAIN_PATH = ROOT / "data" / "processed" / "train.csv"
VALIDATION_PATH = ROOT / "data" / "processed" / "validation.csv"

MODEL_DIR = ROOT / "models" / "candidates"
REPORT_DIR = ROOT / "reports" / "evaluation"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
TARGET = "target_low_score"

CATEGORICAL_FEATURES = [
    "code_module",
    "code_presentation",
    "target_assessment_type",
]

NUMERIC_FEATURES = [
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

FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES


# --------------------------------------------------
# 2. Load data
# --------------------------------------------------

print("=" * 65)
print("ADVANCED STUDENT AT-RISK MODEL COMPARISON")
print("=" * 65)

train_df = pd.read_csv(TRAIN_PATH)
validation_df = pd.read_csv(VALIDATION_PATH)

required_columns = FEATURES + [TARGET]

for column in required_columns:
    if column not in train_df.columns:
        raise ValueError(f"Missing training column: {column}")
    if column not in validation_df.columns:
        raise ValueError(f"Missing validation column: {column}")

X_train = train_df[FEATURES].copy()
y_train = train_df[TARGET].astype(int)

X_val = validation_df[FEATURES].copy()
y_val = validation_df[TARGET].astype(int)

if set(y_train.unique()) != {0, 1}:
    raise ValueError("Training target must contain both 0 and 1.")

if set(y_val.unique()) != {0, 1}:
    raise ValueError("Validation target must contain both 0 and 1.")

# Convert categorical values to strings consistently.
for column in CATEGORICAL_FEATURES:
    X_train[column] = X_train[column].fillna("Unknown").astype(str)
    X_val[column] = X_val[column].fillna("Unknown").astype(str)

print(f"\nTraining rows: {len(X_train):,}")
print(f"Validation rows: {len(X_val):,}")
print(f"Training positives: {int(y_train.sum()):,}")
print(f"Validation positives: {int(y_val.sum()):,}")
print(f"Features used: {len(FEATURES)}")


# --------------------------------------------------
# 3. Shared preprocessing
# --------------------------------------------------

categorical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ]
)

numeric_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("categorical", categorical_transformer, CATEGORICAL_FEATURES),
        ("numeric", numeric_transformer, NUMERIC_FEATURES),
    ],
    remainder="drop",
)


# --------------------------------------------------
# 4. Define candidate models
# --------------------------------------------------

negative_count = int((y_train == 0).sum())
positive_count = int((y_train == 1).sum())
scale_pos_weight = negative_count / positive_count

models = {
    "random_forest": RandomForestClassifier(
        n_estimators=300,
        max_depth=15,
        min_samples_leaf=5,
        class_weight="balanced_subsample",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),

    "lightgbm": LGBMClassifier(
        n_estimators=500,
        learning_rate=0.03,
        num_leaves=31,
        max_depth=-1,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbosity=-1,
    ),

    "xgboost": XGBClassifier(
        n_estimators=500,
        learning_rate=0.03,
        max_depth=6,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        objective="binary:logistic",
        eval_metric="aucpr",
        tree_method="hist",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),

    "catboost": CatBoostClassifier(
        iterations=500,
        learning_rate=0.05,
        depth=6,
        loss_function="Logloss",
        eval_metric="PRAUC",
        auto_class_weights="Balanced",
        random_seed=RANDOM_STATE,
        thread_count=-1,
        verbose=False,
        allow_writing_files=False,
    ),
}


# --------------------------------------------------
# 5. Threshold tuning on validation data
# --------------------------------------------------

def find_best_f1_threshold(y_true, probabilities):
    precision_values, recall_values, thresholds = (
        precision_recall_curve(y_true, probabilities)
    )

    if len(thresholds) == 0:
        return 0.5

    f1_values = (
        2 * precision_values[:-1] * recall_values[:-1]
        / (
            precision_values[:-1] + recall_values[:-1] + 1e-12
        )
    )

    best_index = int(np.argmax(f1_values))

    return float(thresholds[best_index])


# --------------------------------------------------
# 6. Train and evaluate candidates
# --------------------------------------------------

results = []
threshold_config = {}

for model_name, classifier in models.items():

    print("\n" + "-" * 65)
    print(f"Training: {model_name.upper()}")
    print("-" * 65)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )

    start_time = time.perf_counter()

    pipeline.fit(X_train, y_train)

    training_seconds = time.perf_counter() - start_time

    # Validation probabilities only.
    inference_start = time.perf_counter()
    probabilities = pipeline.predict_proba(X_val)[:, 1]
    inference_seconds = time.perf_counter() - inference_start

    # Select threshold using validation F1.
    best_threshold = find_best_f1_threshold(y_val, probabilities)

    predictions = (probabilities >= best_threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_val, predictions, labels=[0, 1]
    ).ravel()

    metrics = {
        "model": model_name,
        "threshold": best_threshold,
        "accuracy": accuracy_score(y_val, predictions),
        "precision": precision_score(
            y_val, predictions, zero_division=0
        ),
        "recall": recall_score(
            y_val, predictions, zero_division=0
        ),
        "f1": f1_score(
            y_val, predictions, zero_division=0
        ),
        "pr_auc": average_precision_score(y_val, probabilities),
        "roc_auc": roc_auc_score(y_val, probabilities),
        "balanced_accuracy": balanced_accuracy_score(
            y_val, predictions
        ),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "training_seconds": training_seconds,
        "validation_inference_seconds": inference_seconds,
        "validation_rows_per_second": (
            len(X_val) / inference_seconds
            if inference_seconds > 0 else None
        ),
    }

    results.append(metrics)

    threshold_config[model_name] = {
        "threshold": best_threshold,
        "features": FEATURES,
        "target": TARGET,
    }

    # Save candidates separately from production models.
    model_path = MODEL_DIR / f"{model_name}.joblib"
    joblib.dump(pipeline, model_path)

    print(f"Threshold: {best_threshold:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1: {metrics['f1']:.4f}")
    print(f"PR-AUC: {metrics['pr_auc']:.4f}")
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    print(f"Training time: {training_seconds:.2f} seconds")
    print(f"Saved: {model_path}")


# --------------------------------------------------
# 7. Save comparison reports
# --------------------------------------------------

results_df = pd.DataFrame(results)
results_df = results_df.sort_values(
    by="pr_auc", ascending=False
)

csv_path = REPORT_DIR / "advanced_model_comparison.csv"
json_path = REPORT_DIR / "advanced_model_comparison.json"
threshold_path = REPORT_DIR / "candidate_thresholds.json"

results_df.to_csv(csv_path, index=False)

with open(json_path, "w", encoding="utf-8") as file:
    json.dump(
        results_df.to_dict(orient="records"),
        file,
        indent=4,
    )

with open(threshold_path, "w", encoding="utf-8") as file:
    json.dump(threshold_config, file, indent=4)

print("\n" + "=" * 65)
print("MODEL COMPARISON COMPLETE")
print("=" * 65)

display_columns = [
    "model",
    "threshold",
    "precision",
    "recall",
    "f1",
    "pr_auc",
    "roc_auc",
    "training_seconds",
    "validation_rows_per_second",
]

print(results_df[display_columns].to_string(index=False))

print("\nReports saved:")
print(csv_path)
print(json_path)
print(threshold_path)

print("\nCandidate models saved in:")
print(MODEL_DIR)

print("\nIMPORTANT:")
print("The final test dataset was not loaded or evaluated.")
print("Existing production model files were not modified.")
