
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw" / "oulad"

print("=" * 70)
print("       NEXT ASSESSMENT TARGET FEASIBILITY ANALYSIS")
print("=" * 70)

# Load required datasets
assessments = pd.read_csv(DATA_DIR / "assessments.csv")
student_assessment = pd.read_csv(
    DATA_DIR / "studentAssessment.csv"
)
student_info = pd.read_csv(DATA_DIR / "studentInfo.csv")

# Keep only dated TMA and CMA assessments
schedule = assessments[
    assessments["assessment_type"].isin(["TMA", "CMA"])
    & assessments["date"].notna()
].copy()

schedule = schedule.sort_values(
    ["code_module", "code_presentation", "date"]
)

# Generate student-course-assessment schedule
student_schedule = student_info[
    ["id_student", "code_module", "code_presentation"]
].merge(
    schedule,
    on=["code_module", "code_presentation"],
    how="inner"
)

# Attach actual assessment outcomes
student_schedule = student_schedule.merge(
    student_assessment[
        ["id_student", "id_assessment", "date_submitted",
         "score", "is_banked"]
    ],
    on=["id_student", "id_assessment"],
    how="left",
    validate="one_to_one"
)

student_schedule = student_schedule.sort_values(
    ["id_student", "code_module", "code_presentation", "date"]
)

print("\n1. SCHEDULE SIZE")
print("Student-assessment schedule rows:",
      f"{len(student_schedule):,}")

print("Unique students:",
      student_schedule["id_student"].nunique())

print("\n2. ASSESSMENT OUTCOME AVAILABILITY")

print("Observed scores:",
      student_schedule["score"].notna().sum())

print("Missing target scores:",
      student_schedule["score"].isna().sum())

# Build candidate prediction examples
candidate_rows = []
no_prior_history = 0
missing_target_outcomes = 0

group_columns = [
    "id_student",
    "code_module",
    "code_presentation"
]

for _, group in student_schedule.groupby(group_columns, sort=False):

    group = group.sort_values("date").reset_index(drop=True)

    for i in range(1, len(group)):

        target = group.iloc[i]

        # Only use historical assessments scheduled before target
        # and submitted before the target assessment date.
        history = group.iloc[:i]

        history = history[
            (history["date"] < target["date"])
            & (history["date_submitted"] < target["date"])
            & history["score"].notna()
        ]

        if history.empty:
            no_prior_history += 1
            continue

        # No observed target score means no supervised label.
        if pd.isna(target["score"]):
            missing_target_outcomes += 1
            continue

        candidate_rows.append({
            "id_student": target["id_student"],
            "code_module": target["code_module"],
            "code_presentation": target["code_presentation"],
            "target_assessment_id": target["id_assessment"],
            "target_assessment_type": target["assessment_type"],
            "target_date": target["date"],
            "previous_scored_assessments": len(history),
            "previous_mean_score": history["score"].mean(),
            "previous_latest_score": history.iloc[-1]["score"],
            "target_score": target["score"],
            "target_low_score": int(target["score"] < 40)
        })

candidates = pd.DataFrame(candidate_rows)

print("\n3. CANDIDATE PREDICTION DATASET")

print("Candidates with observed target scores:",
      f"{len(candidates):,}")

print("Potential targets without observed scores but with history:",
      f"{missing_target_outcomes:,}")

print("Scheduled assessments without prior scored history:",
      f"{no_prior_history:,}")

if not candidates.empty:

    print("\n4. TARGET CLASS DISTRIBUTION")

    print(
        candidates["target_low_score"]
        .value_counts()
        .rename(index={0: "Score >= 40", 1: "Score < 40"})
    )

    print("\nClass percentages:")

    print(
        (candidates["target_low_score"]
         .value_counts(normalize=True) * 100).round(2)
    )

    print("\n5. ASSESSMENT TYPE DISTRIBUTION")

    print(
        candidates.groupby("target_assessment_type")
        ["target_low_score"]
        .agg(["count", "sum", "mean"])
    )

    print("\n6. STUDENT COVERAGE")

    print("Unique students in candidate dataset:",
          candidates["id_student"].nunique())

    # Save preliminary analysis output
    output_dir = BASE_DIR / "data" / "interim"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "target_feasibility.csv"
    candidates.to_csv(output_file, index=False)

    print("\nPreliminary candidate file saved to:")
    print(output_file)

else:
    print("\nNo candidate examples were generated.")

print("\n" + "=" * 70)
print("       TARGET FEASIBILITY ANALYSIS COMPLETED")
print("=" * 70)
