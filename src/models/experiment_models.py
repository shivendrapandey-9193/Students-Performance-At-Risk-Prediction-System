"""
Comprehensive model experimentation and benchmark script for Student Insight AI.
Evaluates:
- Random Forest
- XGBoost
- LightGBM
- CatBoost
- Gradient Boosting
- Extra Trees
- Logistic Regression

Features:
- Engineered engagement signals (momentum, velocity, consistency, click intensity)
- Class weighting & threshold calibration on Validation set (2014B)
- Final unbiased evaluation on Test set (2014J)
"""

from pathlib import Path
import json
import time
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
)

from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
)
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
import joblib

ROOT = Path("E:/Student-At-Risk-Prediction")
TRAIN_FILE = ROOT / "data" / "processed" / "train.csv"
VAL_FILE = ROOT / "data" / "processed" / "validation.csv"
TEST_FILE = ROOT / "data" / "processed" / "test.csv"
REPORT_DIR = ROOT / "reports" / "evaluation"
MODEL_DIR = ROOT / "models" / "candidates"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "target_low_score"

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer domain-specific academic engagement signals."""
    d = df.copy()
    
    # 1. Click momentum (recency weighting)
    d["click_momentum_7_30"] = (d["clicks_last_7_days"] * 4.0) / (d["clicks_last_30_days"] + 1.0)
    
    # 2. Activity intensity (clicks per interaction record)
    d["clicks_per_activity_record"] = d["total_clicks"] / (d["activity_records"] + 1.0)
    
    # 3. Monthly study consistency (proportion of days active in past month)
    d["consistency_last_30d"] = d["active_days_last_30_days"] / 30.0
    
    # 4. Long-term activity density (active days relative to days elapsed)
    d["engagement_density"] = d["active_days"] / (np.maximum(d["target_date"], 1.0))
    
    # 5. Engagement velocity decline (7-day daily rate vs 30-day daily rate)
    rate_7d = d["clicks_last_7_days"] / 7.0
    rate_30d = d["clicks_last_30_days"] / 30.0
    d["velocity_ratio"] = (rate_7d + 1e-4) / (rate_30d + 1e-4)
    
    return d

if __name__ == "__main__":
    print("Loading datasets...")
    train_raw = pd.read_csv(TRAIN_FILE)
val_raw = pd.read_csv(VAL_FILE)
test_raw = pd.read_csv(TEST_FILE)

train = add_features(train_raw)
val = add_features(val_raw)
test = add_features(test_raw)

cat_features = ["code_module", "code_presentation", "target_assessment_type"]
base_num_features = [
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
engineered_num_features = [
    "click_momentum_7_30",
    "clicks_per_activity_record",
    "consistency_last_30d",
    "engagement_density",
    "velocity_ratio",
]

num_features = base_num_features + engineered_num_features
all_features = cat_features + num_features

print(f"Features ({len(all_features)} total): {all_features}")

X_train = train[all_features]
y_train = train[TARGET].values

X_val = val[all_features]
y_val = val[TARGET].values

X_test = test[all_features]
y_test = test[TARGET].values

# Compute class weight for positive class
neg_count = np.sum(y_train == 0)
pos_count = np.sum(y_train == 1)
scale_pos_weight = neg_count / pos_count
print(f"Train class balance: Neg={neg_count}, Pos={pos_count}, ScalePosWeight={scale_pos_weight:.2f}")

# Preprocessor
preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features),
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]), num_features),
])

print("Fitting preprocessor...")
X_train_proc = preprocessor.fit_transform(X_train)
X_val_proc = preprocessor.transform(X_val)
X_test_proc = preprocessor.transform(X_test)

models = {
    "CatBoost": CatBoostClassifier(
        iterations=400,
        depth=6,
        learning_rate=0.06,
        auto_class_weights="Balanced",
        random_seed=42,
        verbose=0,
    ),
    "LightGBM": LGBMClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        num_leaves=31,
        class_weight="balanced",
        random_state=42,
        verbosity=-1,
        n_jobs=-1,
    ),
    "XGBoost": XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric="logloss",
        n_jobs=-1,
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_leaf=5,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    ),
    "Extra Trees": ExtraTreesClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.08,
        random_state=42,
    ),
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    ),
}

results = []

def evaluate_threshold(y_true, y_prob, threshold):
    y_pred = (y_prob >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "pr_auc": float(average_precision_score(y_true, y_prob)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }

trained_models = {}

print("\n" + "="*80)
print(f"{'Model':<20} | {'ROC-AUC':<8} | {'PR-AUC':<8} | {'Best Thresh':<11} | {'Acc':<7} | {'Prec':<7} | {'Rec':<7} | {'F1':<7}")
print("="*80)

for name, clf in models.items():
    t0 = time.time()
    clf.fit(X_train_proc, y_train)
    fit_time = time.time() - t0
    
    # Predict probabilities on validation
    val_probs = clf.predict_proba(X_val_proc)[:, 1]
    
    # Grid search threshold on validation data to achieve >= 90% accuracy while maximizing F1
    best_thresh = 0.5
    best_eval = None
    best_score = -1.0
    
    # Scan candidate thresholds from 0.30 to 0.85
    candidate_thresholds = np.linspace(0.30, 0.85, 111)
    for th in candidate_thresholds:
        ev = evaluate_threshold(y_val, val_probs, th)
        # Condition: accuracy >= 0.90
        # Priority objective: maximize F1-score subject to accuracy >= 0.90
        if ev["accuracy"] >= 0.90:
            score = ev["f1"]
            if score > best_score:
                best_score = score
                best_thresh = th
                best_eval = ev
                
    if best_eval is None: # Fallback if >= 90% wasn't met in range
        best_thresh = 0.5
        best_eval = evaluate_threshold(y_val, val_probs, 0.5)
        
    print(f"{name:<20} | {best_eval['roc_auc']:.4f}   | {best_eval['pr_auc']:.4f}   | {best_thresh:<11.4f} | {best_eval['accuracy']*100:5.2f}% | {best_eval['precision']*100:5.2f}% | {best_eval['recall']*100:5.2f}% | {best_eval['f1']*100:5.2f}%")
    
    trained_models[name] = {
        "model": clf,
        "best_threshold": float(best_thresh),
        "val_metrics": best_eval,
        "fit_time": fit_time,
    }
    
    results.append({
        "model": name,
        "validation_accuracy": best_eval["accuracy"],
        "validation_precision": best_eval["precision"],
        "validation_recall": best_eval["recall"],
        "validation_f1": best_eval["f1"],
        "validation_roc_auc": best_eval["roc_auc"],
        "validation_pr_auc": best_eval["pr_auc"],
        "validation_balanced_accuracy": best_eval["balanced_accuracy"],
        "optimal_threshold": float(best_thresh),
        "confusion_matrix": {
            "tn": best_eval["tn"], "fp": best_eval["fp"],
            "fn": best_eval["fn"], "tp": best_eval["tp"]
        },
        "training_seconds": round(fit_time, 2)
    })

# Select champion based on highest validation F1 with >= 90% accuracy and highest ROC-AUC
champion_name = max(results, key=lambda r: (r["validation_accuracy"] >= 0.90, r["validation_f1"], r["validation_roc_auc"]))["model"]
champion_info = trained_models[champion_name]

print("\n" + "="*80)
print(f"CHAMPION MODEL SELECTED: {champion_name}")
print(f"Optimal Validation Threshold: {champion_info['best_threshold']:.4f}")
print("="*80)

# Evaluate Champion Model on untouched TEST set (2014J)
test_probs = champion_info["model"].predict_proba(X_test_proc)[:, 1]
test_eval = evaluate_threshold(y_test, test_probs, champion_info["best_threshold"])

print("\nFINAL UNBIASED TEST EVALUATION (2014J):")
print(f"Accuracy:          {test_eval['accuracy']*100:.2f}%")
print(f"Precision:         {test_eval['precision']*100:.2f}%")
print(f"Recall:            {test_eval['recall']*100:.2f}%")
print(f"F1-Score:          {test_eval['f1']*100:.2f}%")
print(f"ROC-AUC:           {test_eval['roc_auc']:.4f}")
print(f"PR-AUC:            {test_eval['pr_auc']:.4f}")
print(f"Balanced Accuracy: {test_eval['balanced_accuracy']*100:.2f}%")
print(f"Confusion Matrix:  TN={test_eval['tn']}, FP={test_eval['fp']}, FN={test_eval['fn']}, TP={test_eval['tp']}")

# Build complete pipeline packaging preprocessor and champion model
full_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", champion_info["model"]),
])

# Save production model
prod_model_path = ROOT / "models" / "candidates" / "production_model.joblib"
try:
    joblib.dump({
        "pipeline": full_pipeline,
        "model_name": champion_name,
        "threshold": champion_info["best_threshold"],
        "features": all_features,
        "val_metrics": champion_info["val_metrics"],
        "test_metrics": test_eval,
    }, prod_model_path)
    print("Saved candidate model to:", prod_model_path)
except Exception as e:
    print(f"Error saving {prod_model_path}: {e}")

# Also save standalone model pipeline
saved_path = ROOT / "models" / "saved" / "production_model.joblib"
try:
    joblib.dump(full_pipeline, saved_path)
    print("Saved pipeline to:", saved_path)
except Exception as e:
    print(f"Error saving {saved_path}: {e}")

# Save detailed benchmark reports
with open(REPORT_DIR / "model_benchmark_comparison.json", "w") as f:
    json.dump(results, f, indent=4)

with open(REPORT_DIR / "improved_model_final_test_metrics.json", "w") as f:
    json.dump({
        "champion_model": champion_name,
        "threshold": champion_info["best_threshold"],
        "test_metrics": test_eval,
        "validation_metrics": champion_info["val_metrics"],
    }, f, indent=4)

print("\nModel saved successfully.")
print("Reports saved to:", REPORT_DIR)
