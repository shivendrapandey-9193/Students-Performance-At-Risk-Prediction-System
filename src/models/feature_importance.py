from pathlib import Path
import joblib
import pandas as pd

from sklearn.inspection import permutation_importance

ROOT = Path(__file__).resolve().parents[2]

VALIDATION_FILE = ROOT / "data" / "processed" / "validation.csv"
MODEL_FILE = ROOT / "models" / "saved" / "random_forest.joblib"
OUTPUT_DIR = ROOT / "reports" / "evaluation"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

# Load validation data and trained model
data = pd.read_csv(VALIDATION_FILE)

X = data[features]
y = data[TARGET]

model = joblib.load(MODEL_FILE)

print("Calculating permutation feature importance...")
print("This may take a few minutes.")

# Measure the impact of shuffling each feature
importance = permutation_importance(
    model,
    X,
    y,
    scoring="average_precision",
    n_repeats=5,
    random_state=42,
    n_jobs=-1,
)

results = pd.DataFrame({
    "feature": features,
    "importance_mean": importance.importances_mean,
    "importance_std": importance.importances_std,
})

results = results.sort_values(
    by="importance_mean",
    ascending=False
)

# Save results
output_file = OUTPUT_DIR / "feature_importance.csv"
results.to_csv(output_file, index=False)

print("\nFEATURE IMPORTANCE RESULTS")
print("=" * 55)

print(results.to_string(index=False))

print("\nSaved:", output_file)
