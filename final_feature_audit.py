
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent

FILE = (
    BASE_DIR
    / "data"
    / "interim"
    / "student_features_final.csv"
)

df = pd.read_csv(FILE)

print("=" * 65)
print("           FINAL FEATURE AND LEAKAGE AUDIT")
print("=" * 65)

# 1. Basic integrity
print("\n1. DATASET INTEGRITY")

print("Shape:", df.shape)
print("Missing values:", df.isna().sum().sum())

print(
    "Duplicate student-target pairs:",
    df.duplicated(
        ["id_student", "target_assessment_id"]
    ).sum()
)

# 2. Target verification
print("\n2. TARGET VERIFICATION")

expected = (df["target_score"] < 40).astype(int)

print(
    "Incorrect target labels:",
    (df["target_low_score"] != expected).sum()
)

print("Target distribution:")
print(df["target_low_score"].value_counts())

# 3. Temporal feature consistency
print("\n3. TEMPORAL FEATURE CONSISTENCY")

checks = {
    "7-day clicks <= 14-day clicks":
        (df["clicks_last_7_days"] <= df["clicks_last_14_days"]).all(),

    "14-day clicks <= 30-day clicks":
        (df["clicks_last_14_days"] <= df["clicks_last_30_days"]).all(),

    "30-day clicks <= total clicks":
        (df["clicks_last_30_days"] <= df["total_clicks"]).all(),

    "30-day active days <= total active days":
        (df["active_days_last_30_days"] <= df["active_days"]).all(),

    "Recent active days <= 30":
        (df["active_days_last_30_days"] <= 30).all(),

    "Zero active days implies zero clicks":
        (
            (df["active_days"] != 0)
            | (df["total_clicks"] == 0)
        ).all()
}

for name, passed in checks.items():
    print(f"{name}: {'PASS' if passed else 'FAIL'}")

# 4. Average clicks consistency
expected_average = (
    df["total_clicks"]
    / df["active_days"].replace(0, np.nan)
).fillna(0)

average_matches = np.isclose(
    df["average_clicks_per_active_day"],
    expected_average
)

print(
    "\nAverage clicks calculation mismatches:",
    (~average_matches).sum()
)

# 5. Leakage audit
print("\n5. MODEL INPUT LEAKAGE AUDIT")

excluded_columns = [
    "id_student",
    "target_assessment_id",
    "target_date",
    "target_score",
    "target_low_score"
]

model_features = [
    column for column in df.columns
    if column not in excluded_columns
]

print("Excluded columns:", excluded_columns)
print("Candidate model features:", model_features)

# 6. Feature and target correlations
print("\n6. FEATURE CORRELATIONS")

numeric_features = [
    "previous_scored_assessments",
    "previous_mean_score",
    "previous_latest_score",
    "total_clicks",
    "activity_records",
    "active_days",
    "active_days_last_30_days",
    "clicks_last_7_days",
    "clicks_last_14_days",
    "clicks_last_30_days",
    "average_clicks_per_active_day"
]

print(
    df[numeric_features + ["target_low_score"]]
    .corr()["target_low_score"]
    .sort_values()
)

# 7. Final summary
print("\n7. AUDIT SUMMARY")

print("Total records:", len(df))
print("Total candidate features:", len(model_features))
print("Target positive rate:",
      round(df["target_low_score"].mean() * 100, 2), "%")

print("\n" + "=" * 65)
print("           FINAL AUDIT COMPLETED")
print("=" * 65)
