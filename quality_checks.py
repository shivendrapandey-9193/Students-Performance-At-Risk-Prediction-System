
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw" / "oulad"

print("=" * 65)
print("           OULAD DATA QUALITY VALIDATION")
print("=" * 65)

# Load smaller datasets
assessments = pd.read_csv(DATA_DIR / "assessments.csv")
courses = pd.read_csv(DATA_DIR / "courses.csv")
student_assessment = pd.read_csv(DATA_DIR / "studentAssessment.csv")
student_info = pd.read_csv(DATA_DIR / "studentInfo.csv")
registration = pd.read_csv(DATA_DIR / "studentRegistration.csv")
vle = pd.read_csv(DATA_DIR / "vle.csv")

# 1. Assessment score validation
print("\n1. ASSESSMENT SCORE VALIDATION")

print("Minimum score:", student_assessment["score"].min())
print("Maximum score:", student_assessment["score"].max())
print("Missing scores:", student_assessment["score"].isna().sum())

invalid_scores = student_assessment[
    (student_assessment["score"] < 0) |
    (student_assessment["score"] > 100)
]

print("Scores outside 0-100:", len(invalid_scores))

# 2. Assessment date validation
print("\n2. ASSESSMENT DATE VALIDATION")

print(
    assessments.groupby("assessment_type")["date"]
    .agg(["count", "min", "max"])
)

print(
    "\nMissing dates by assessment type:"
)

print(
    assessments[assessments["date"].isna()]
    ["assessment_type"].value_counts()
)

# 3. Key validation
print("\n3. KEY VALIDATION")

print(
    "Duplicate assessment IDs:",
    assessments["id_assessment"].duplicated().sum()
)

print(
    "Duplicate student-course records:",
    student_info.duplicated(
        subset=["id_student", "code_module", "code_presentation"]
    ).sum()
)

print(
    "Duplicate registration records:",
    registration.duplicated(
        subset=["id_student", "code_module", "code_presentation"]
    ).sum()
)

print(
    "Duplicate student-assessment keys:",
    student_assessment.duplicated(
        subset=["id_student", "id_assessment"]
    ).sum()
)

# 4. Relationship validation
print("\n4. RELATIONSHIP VALIDATION")

assessment_ids = set(assessments["id_assessment"])

print(
    "Unknown assessment IDs in studentAssessment:",
    (~student_assessment["id_assessment"].isin(assessment_ids)).sum()
)

print(
    "Unknown course presentations in studentInfo:",
    (~pd.MultiIndex.from_frame(
        student_info[["code_module", "code_presentation"]]
    ).isin(
        pd.MultiIndex.from_frame(
            courses[["code_module", "code_presentation"]]
        )
    )).sum()
)

# 5. Registration validation
print("\n5. REGISTRATION VALIDATION")

print(
    "Missing registration dates:",
    registration["date_registration"].isna().sum()
)

print(
    "Missing unregistration dates:",
    registration["date_unregistration"].isna().sum()
)

# 6. VLE metadata validation
print("\n6. VLE METADATA VALIDATION")

print("Unique VLE site IDs:", vle["id_site"].nunique())
print("Total VLE metadata rows:", len(vle))

print(
    "Duplicate VLE site IDs within course presentation:",
    vle.duplicated(
        subset=["id_site", "code_module", "code_presentation"]
    ).sum()
)

# 7. VLE activity validation (large file, chunk processing)
print("\n7. STUDENT VLE ACTIVITY VALIDATION")

vle_path = DATA_DIR / "studentVle.csv"

total_rows = 0
negative_clicks = 0
negative_dates = 0
max_clicks = 0

for chunk in pd.read_csv(vle_path, chunksize=500_000):

    total_rows += len(chunk)

    negative_clicks += (chunk["sum_click"] < 0).sum()
    negative_dates += (chunk["date"] < 0).sum()

    max_clicks = max(
        max_clicks,
        chunk["sum_click"].max()
    )

print("Total activity records:", f"{total_rows:,}")
print("Negative click values:", negative_clicks)
print("Negative activity dates:", negative_dates)
print("Maximum clicks in a record:", max_clicks)

print("\n" + "=" * 65)
print("          QUALITY VALIDATION COMPLETED")
print("=" * 65)
