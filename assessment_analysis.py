
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw" / "oulad"

# Load datasets
assessments = pd.read_csv(DATA_DIR / "assessments.csv")
student_assessment = pd.read_csv(
    DATA_DIR / "studentAssessment.csv"
)

print("=" * 70)
print("              ASSESSMENT ANALYSIS")
print("=" * 70)

# 1. Assessment distribution
print("\n1. ASSESSMENT TYPE DISTRIBUTION")

print(
    assessments["assessment_type"].value_counts()
)

# 2. Assessment schedule
print("\n2. ASSESSMENT SCHEDULE")

print(
    assessments.groupby(
        ["code_module", "code_presentation", "assessment_type"]
    )["date"].agg(["count", "min", "max"])
)

# 3. Missing scores
print("\n3. MISSING ASSESSMENT SCORES")

missing = student_assessment[
    student_assessment["score"].isna()
]

print("Total missing scores:", len(missing))

print(
    missing.groupby("id_assessment")
    .size()
    .sort_values(ascending=False)
    .head(15)
)

# 4. Join student scores with assessment information
merged = student_assessment.merge(
    assessments,
    on="id_assessment",
    how="left",
    validate="many_to_one"
)

print("\n4. SCORE DISTRIBUTION BY ASSESSMENT TYPE")

print(
    merged.groupby("assessment_type")["score"]
    .agg(["count", "mean", "min", "max"])
)

# 5. TMA and CMA target eligibility
eligible = assessments[
    assessments["assessment_type"].isin(["TMA", "CMA"])
    & assessments["date"].notna()
].copy()

eligible = eligible.sort_values(
    ["code_module", "code_presentation", "date"]
)

print("\n5. ELIGIBLE FUTURE ASSESSMENTS")

print("Total eligible assessments:", len(eligible))

print(
    eligible.groupby("assessment_type")
    .size()
)

# 6. Students with scored TMA/CMA records
scored = merged[
    merged["assessment_type"].isin(["TMA", "CMA"])
    & merged["score"].notna()
]

print("\n6. STUDENT PERFORMANCE RECORDS")

print("Scored TMA/CMA records:", len(scored))

print(
    "Unique students with scored TMA/CMA:",
    scored["id_student"].nunique()
)

print(
    "Students with scores below 40:",
    scored.loc[scored["score"] < 40, "id_student"].nunique()
)

print("\n" + "=" * 70)
print("              ANALYSIS COMPLETED")
print("=" * 70)
