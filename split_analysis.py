
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

FILE = (
    BASE_DIR
    / "data"
    / "interim"
    / "student_features_final.csv"
)

df = pd.read_csv(FILE)

print("=" * 65)
print("       TRAIN / TEST SPLIT ANALYSIS")
print("=" * 65)

# 1. Course presentation distribution
print("\n1. RECORDS BY PRESENTATION")

summary = (
    df.groupby("code_presentation")
    .agg(
        total_records=("target_low_score", "size"),
        at_risk=("target_low_score", "sum"),
        unique_students=("id_student", "nunique"),
        risk_rate=("target_low_score", "mean")
    )
)

summary["risk_rate"] = (summary["risk_rate"] * 100).round(2)

print(summary)

# 2. Module distribution
print("\n2. RECORDS BY MODULE AND PRESENTATION")

print(
    df.groupby(
        ["code_module", "code_presentation"]
    )["target_low_score"]
    .agg(["count", "sum", "mean"])
    .round(3)
)

# 3. Chronological presentation order
print("\n3. PRESENTATION ORDER")

presentations = sorted(df["code_presentation"].unique())

for position, presentation in enumerate(presentations, start=1):
    print(position, "->", presentation)

# 4. Student overlap between presentations
print("\n4. STUDENT OVERLAP")

for i, first in enumerate(presentations):
    first_students = set(
        df.loc[
            df["code_presentation"] == first,
            "id_student"
        ]
    )

    for second in presentations[i + 1:]:
        second_students = set(
            df.loc[
                df["code_presentation"] == second,
                "id_student"
            ]
        )

        overlap = len(first_students & second_students)

        print(f"{first} vs {second}: {overlap:,} shared students")

# 5. Final dataset information
print("\n5. OVERALL DATASET")

print("Total records:", len(df))
print("Unique students:", df["id_student"].nunique())
print("Positive examples:", df["target_low_score"].sum())
print(
    "Positive rate:",
    round(df["target_low_score"].mean() * 100, 2),
    "%"
)

print("\n" + "=" * 65)
print("       SPLIT ANALYSIS COMPLETED")
print("=" * 65)
