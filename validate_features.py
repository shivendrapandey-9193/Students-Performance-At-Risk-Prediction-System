
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "interim" / "student_features.csv"

df = pd.read_csv(DATA_FILE)

print("=" * 65)
print("       FEATURE DATASET VALIDATION")
print("=" * 65)

# 1. Dataset dimensions
print("\n1. DATASET DIMENSIONS")
print("Rows:", f"{len(df):,}")
print("Columns:", len(df.columns))

# 2. Duplicate prediction examples
print("\n2. DUPLICATE CHECK")

duplicate_count = df.duplicated(
    subset=["id_student", "target_assessment_id"]
).sum()

print("Duplicate student-target pairs:", duplicate_count)

# 3. Target validation
print("\n3. TARGET VALIDATION")

print("Target values:")
print(df["target_low_score"].value_counts())

print("\nTarget percentages:")
print(
    (df["target_low_score"].value_counts(normalize=True) * 100)
    .round(2)
)

expected_target = (df["target_score"] < 40).astype(int)

print(
    "Incorrect target labels:",
    (df["target_low_score"] != expected_target).sum()
)

# 4. Feature range validation
print("\n4. FEATURE RANGE CHECKS")

for column in [
    "previous_scored_assessments",
    "previous_mean_score",
    "previous_latest_score",
    "total_clicks",
    "activity_records"
]:
    print(
        f"{column}: min={df[column].min()}, "
        f"max={df[column].max()}"
    )

# 5. Missing and infinite values
print("\n5. MISSING VALUE CHECK")

print(df.isnull().sum())

numeric = df.select_dtypes(include="number")

print(
    "Infinite numeric values:",
    int(numeric.isin([float("inf"), float("-inf")]).sum().sum())
)

# 6. Zero engagement
print("\n6. ENGAGEMENT CHECK")

print("Records with zero clicks:", (df["total_clicks"] == 0).sum())
print(
    "Records with zero activity records:",
    (df["activity_records"] == 0).sum()
)

# 7. Assessment type breakdown
print("\n7. TARGET BY ASSESSMENT TYPE")

print(
    df.groupby("target_assessment_type")["target_low_score"]
    .agg(["count", "sum", "mean"])
)

# 8. Model input columns
print("\n8. MODEL FEATURE CANDIDATES")

excluded = [
    "id_student",
    "target_assessment_id",
    "target_date",
    "target_score",
    "target_low_score"
]

feature_columns = [
    col for col in df.columns
    if col not in excluded
]

print(feature_columns)

print("\nTarget column: target_low_score")
print("Outcome audit column: target_score")

print("\n" + "=" * 65)
print("       FEATURE VALIDATION COMPLETED")
print("=" * 65)

