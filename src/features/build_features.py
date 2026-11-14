
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw" / "oulad"
INTERIM_DIR = BASE_DIR / "data" / "interim"

CANDIDATE_FILE = INTERIM_DIR / "target_feasibility.csv"
VLE_FILE = RAW_DIR / "studentVle.csv"

OUTPUT_FILE = INTERIM_DIR / "student_features.csv"

CHUNK_SIZE = 250_000

print("=" * 65)
print("       STUDENT FEATURE ENGINEERING")
print("=" * 65)

# Load candidate prediction examples
candidates = pd.read_csv(CANDIDATE_FILE)

candidates["snapshot_id"] = range(len(candidates))

print("\nCandidate records:", len(candidates))

# Keep only fields needed to match VLE records
targets = candidates[
    [
        "snapshot_id",
        "id_student",
        "code_module",
        "code_presentation",
        "target_date"
    ]
].copy()

targets["target_date"] = pd.to_numeric(
    targets["target_date"]
)

# Prepare aggregation storage
click_totals = {}
activity_totals = {}

print("\nProcessing studentVle.csv in chunks...")

for chunk_number, chunk in enumerate(
    pd.read_csv(VLE_FILE, chunksize=CHUNK_SIZE),
    start=1
):

    # Match student, module and presentation
    matched = chunk.merge(
        targets,
        on=[
            "id_student",
            "code_module",
            "code_presentation"
        ],
        how="inner"
    )

    # Keep activity strictly before prediction cutoff
    matched = matched[
        matched["date"] < matched["target_date"]
    ]

    if not matched.empty:

        grouped = matched.groupby("snapshot_id").agg(
            total_clicks=("sum_click", "sum"),
            activity_records=("sum_click", "size")
        )

        for snapshot_id, row in grouped.iterrows():

            sid = int(snapshot_id)

            click_totals[sid] = (
                click_totals.get(sid, 0)
                + int(row["total_clicks"])
            )

            activity_totals[sid] = (
                activity_totals.get(sid, 0)
                + int(row["activity_records"])
            )

    print(f"Processed chunk {chunk_number}")

# Attach calculated engagement features
candidates["total_clicks"] = (
    candidates["snapshot_id"]
    .map(click_totals)
    .fillna(0)
    .astype("int64")
)

candidates["activity_records"] = (
    candidates["snapshot_id"]
    .map(activity_totals)
    .fillna(0)
    .astype("int64")
)

# Remove internal snapshot identifier
candidates.drop(columns=["snapshot_id"], inplace=True)

# Separate output columns
candidates.to_csv(OUTPUT_FILE, index=False)

print("\nFeature engineering completed.")

print("Output file:", OUTPUT_FILE)

print("\nOutput shape:", candidates.shape)

print("\nGenerated features:")
print(candidates.columns.tolist())

print("\nMissing values:")
print(candidates.isnull().sum())

print("\n" + "=" * 65)
print("       FEATURE ENGINEERING COMPLETED")
print("=" * 65)
