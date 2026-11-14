
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent

INPUT_FILE = ROOT / "data" / "interim" / "student_features_final.csv"
OUTPUT_DIR = ROOT / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

# Chronological presentation split
train_presentations = ["2013B", "2013J"]
validation_presentation = "2014B"
test_presentation = "2014J"

train = df[df["code_presentation"].isin(train_presentations)].copy()
validation = df[df["code_presentation"] == validation_presentation].copy()
test = df[df["code_presentation"] == test_presentation].copy()

# Verify that all splits contain data
assert len(train) > 0
assert len(validation) > 0
assert len(test) > 0

# Verify chronological separation
assert set(train["code_presentation"]).isdisjoint(
    set(validation["code_presentation"])
)
assert set(train["code_presentation"]).isdisjoint(
    set(test["code_presentation"])
)
assert set(validation["code_presentation"]).isdisjoint(
    set(test["code_presentation"])
)

# Save the datasets
train.to_csv(OUTPUT_DIR / "train.csv", index=False)
validation.to_csv(OUTPUT_DIR / "validation.csv", index=False)
test.to_csv(OUTPUT_DIR / "test.csv", index=False)

# Print split summary
for name, data in [
    ("TRAIN", train),
    ("VALIDATION", validation),
    ("TEST", test),
]:
    positives = int(data["target_low_score"].sum())

    print(f"\n{name}")
    print("-" * 40)
    print("Rows:", len(data))
    print("Unique students:", data["id_student"].nunique())
    print("At-risk examples:", positives)
    print("Normal examples:", len(data) - positives)
    print("Risk rate:", round(100 * positives / len(data), 2), "%")

print("\nSplit files saved successfully.")
