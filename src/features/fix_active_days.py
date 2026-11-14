
from pathlib import Path
import pandas as pd
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw" / "oulad"
INTERIM_DIR = BASE_DIR / "data" / "interim"

INPUT_FILE = INTERIM_DIR / "student_features_enriched.csv"
VLE_FILE = RAW_DIR / "studentVle.csv"
OUTPUT_FILE = INTERIM_DIR / "student_features_final.csv"

CHUNK_SIZE = 250_000

print("=" * 65)
print("       CORRECTING UNIQUE ACTIVE DAY FEATURES")
print("=" * 65)

df = pd.read_csv(INPUT_FILE)

df["snapshot_id"] = range(len(df))

targets = df[
    [
        "snapshot_id",
        "id_student",
        "code_module",
        "code_presentation",
        "target_date"
    ]
].copy()

# Store dates in sets to avoid counting the same day twice
all_active_dates = defaultdict(set)
recent_active_dates = defaultdict(set)

print("\nProcessing VLE records...")

for chunk_number, chunk in enumerate(
    pd.read_csv(VLE_FILE, chunksize=CHUNK_SIZE),
    start=1
):
    matched = chunk.merge(
        targets,
        on=[
            "id_student",
            "code_module",
            "code_presentation"
        ],
        how="inner"
    )

    matched = matched[
        matched["date"] < matched["target_date"]
    ]

    if not matched.empty:

        # Keep only the unique snapshot/date combinations
        activity = matched[
            ["snapshot_id", "date", "target_date"]
        ].drop_duplicates()

        for row in activity.itertuples(index=False):

            sid = int(row.snapshot_id)
            activity_date = int(row.date)
            target_date = int(row.target_date)

            all_active_dates[sid].add(activity_date)

            if target_date - 30 <= activity_date < target_date:
                recent_active_dates[sid].add(activity_date)

    print(f"Processed chunk {chunk_number}")

# Correct the unique day counts
df["active_days"] = [
    len(all_active_dates.get(i, set()))
    for i in df["snapshot_id"]
]

df["active_days_last_30_days"] = [
    len(recent_active_dates.get(i, set()))
    for i in df["snapshot_id"]
]

df = df.drop(columns=["snapshot_id"])

df.to_csv(OUTPUT_FILE, index=False)

print("\nCorrected dataset:", OUTPUT_FILE)
print("Dataset shape:", df.shape)

print("\nActive day statistics:")
print(
    df[
        ["active_days", "active_days_last_30_days"]
    ].describe()
)

print("\n" + "=" * 65)
print("       ACTIVE DAY CORRECTION COMPLETED")
print("=" * 65)
