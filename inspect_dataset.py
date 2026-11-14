
from pathlib import Path
import pandas as pd

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw" / "oulad"

FILES = [
    "assessments.csv",
    "courses.csv",
    "studentAssessment.csv",
    "studentInfo.csv",
    "studentRegistration.csv",
    "studentVle.csv",
    "vle.csv"
]

print("=" * 65)
print("       OULAD DATASET INSPECTION")
print("=" * 65)

for filename in FILES:
    file_path = DATA_DIR / filename

    print(f"\n\n{'-' * 65}")
    print(f"FILE: {filename}")
    print(f"SIZE: {file_path.stat().st_size / (1024**2):.2f} MB")
    print("-" * 65)

    if filename == "studentVle.csv":
        # Large file: process in chunks to reduce memory usage
        total_rows = 0
        missing_values = None
        columns = None

        for chunk in pd.read_csv(file_path, chunksize=500_000):
            total_rows += len(chunk)

            if columns is None:
                columns = chunk.columns.tolist()
                missing_values = pd.Series(0, index=columns)

            missing_values += chunk.isnull().sum()

        print("Total rows:", f"{total_rows:,}")
        print("Columns:", columns)
        print("\nMissing values:")
        print(missing_values)

        print("\nNote: Full duplicate checking is postponed.")

    else:
        df = pd.read_csv(file_path)

        print("Rows:", f"{len(df):,}")
        print("Columns:", len(df.columns))
        print("\nColumn names:")
        print(df.columns.tolist())

        print("\nData types:")
        print(df.dtypes)

        print("\nMissing values:")
        print(df.isnull().sum())

        print("\nDuplicate rows:", df.duplicated().sum())

print("\n\n" + "=" * 65)
print("       DATASET INSPECTION COMPLETED")
print("=" * 65)
