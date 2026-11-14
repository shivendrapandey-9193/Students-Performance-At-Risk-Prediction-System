
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw" / "oulad"
INTERIM_DIR = BASE_DIR / "data" / "interim"

INPUT_FILE = INTERIM_DIR / "student_features.csv"
VLE_FILE = RAW_DIR / "studentVle.csv"
OUTPUT_FILE = INTERIM_DIR / "student_features_enriched.csv"

CHUNK_SIZE = 250_000

print("=" * 65)
print("       TEMPORAL ENGAGEMENT FEATURE ENGINEERING")
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

targets["target_date"] = pd.to_numeric(targets["target_date"])

# Aggregation dictionaries
total_active_days = {}
active_days_30 = {}
clicks_7 = {}
clicks_14 = {}
clicks_30 = {}

print("\nProcessing VLE activity in chunks...")

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

    # Strictly before target date
    matched = matched[
        matched["date"] < matched["target_date"]
    ]

    if not matched.empty:

        # Unique active dates per prediction snapshot
        daily = (
            matched.groupby(["snapshot_id", "date"])["sum_click"]
            .sum()
            .reset_index()
        )

        for snapshot_id, group in daily.groupby("snapshot_id"):

            sid = int(snapshot_id)

            total_active_days[sid] = (
                total_active_days.get(sid, 0) + len(group)
            )

            target_date = targets.loc[
                targets["snapshot_id"] == sid,
                "target_date"
            ].iloc[0]

            last_7 = group[group["date"] >= target_date - 7]
            last_14 = group[group["date"] >= target_date - 14]
            last_30 = group[group["date"] >= target_date - 30]

            clicks_7[sid] = (
                clicks_7.get(sid, 0)
                + int(last_7["sum_click"].sum())
            )

            clicks_14[sid] = (
                clicks_14.get(sid, 0)
                + int(last_14["sum_click"].sum())
            )

            clicks_30[sid] = (
                clicks_30.get(sid, 0)
                + int(last_30["sum_click"].sum())
            )

            active_days_30[sid] = (
                active_days_30.get(sid, 0)
                + len(last_30)
            )

    print(f"Processed chunk {chunk_number}")

# Attach features
df["active_days"] = (
    df["snapshot_id"].map(total_active_days).fillna(0).astype(int)
)

df["active_days_last_30_days"] = (
    df["snapshot_id"].map(active_days_30).fillna(0).astype(int)
)

df["clicks_last_7_days"] = (
    df["snapshot_id"].map(clicks_7).fillna(0).astype(int)
)

df["clicks_last_14_days"] = (
    df["snapshot_id"].map(clicks_14).fillna(0).astype(int)
)

df["clicks_last_30_days"] = (
    df["snapshot_id"].map(clicks_30).fillna(0).astype(int)
)

df["average_clicks_per_active_day"] = (
    df["total_clicks"] / df["active_days"].replace(0, pd.NA)
).fillna(0)

df.drop(columns=["snapshot_id"], inplace=True)

df.to_csv(OUTPUT_FILE, index=False)

print("\nOutput shape:", df.shape)
print("\nNew features:")
print([
    "active_days",
    "active_days_last_30_days",
    "clicks_last_7_days",
    "clicks_last_14_days",
    "clicks_last_30_days",
    "average_clicks_per_active_day"
])

print("\nSaved:", OUTPUT_FILE)

print("\n" + "=" * 65)
print("       TEMPORAL FEATURES COMPLETED")
print("=" * 65)
