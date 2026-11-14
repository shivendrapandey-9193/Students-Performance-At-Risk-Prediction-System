from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed"

train = pd.read_csv(DATA_DIR / "train.csv")
validation = pd.read_csv(DATA_DIR / "validation.csv")
test = pd.read_csv(DATA_DIR / "test.csv")

train_students = set(train["id_student"].unique())
validation_students = set(validation["id_student"].unique())
test_students = set(test["id_student"].unique())

development_students = train_students | validation_students

seen_test_students = test_students & development_students
unseen_test_students = test_students - development_students

print("=" * 55)
print("UNSEEN STUDENT GENERALIZATION ANALYSIS")
print("=" * 55)

print("\nTraining students:", len(train_students))
print("Validation students:", len(validation_students))
print("Test students:", len(test_students))

print("\nTest students previously seen in train/validation:",
      len(seen_test_students))

print("Completely unseen test students:",
      len(unseen_test_students))

print("Unseen student percentage:",
      round(100 * len(unseen_test_students) / len(test_students), 2), "%")

# Separate test rows into seen and unseen groups
test_unseen = test[test["id_student"].isin(unseen_test_students)].copy()
test_seen = test[test["id_student"].isin(seen_test_students)].copy()

print("\nTEST ROW ANALYSIS")
print("-" * 40)

for name, data in [
    ("Seen students", test_seen),
    ("Unseen students", test_unseen),
]:
    positives = int(data["target_low_score"].sum())

    print(f"\n{name}")
    print("Rows:", len(data))
    print("Unique students:", data["id_student"].nunique())
    print("At-risk examples:", positives)
    print("Risk rate:",
          round(100 * positives / len(data), 2) if len(data) else 0, "%")

# Save subsets for a separate evaluation
test_seen.to_csv(DATA_DIR / "test_seen_students.csv", index=False)
test_unseen.to_csv(DATA_DIR / "test_unseen_students.csv", index=False)

print("\nSaved:")
print(DATA_DIR / "test_seen_students.csv")
print(DATA_DIR / "test_unseen_students.csv")
