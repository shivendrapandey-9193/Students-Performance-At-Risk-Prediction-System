
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "data" / "interim" / "student_features.csv"
FIGURE_DIR = BASE_DIR / "reports" / "figures"

FIGURE_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE)

sns.set_theme(style="whitegrid")

print("=" * 65)
print("          EXPLORATORY DATA ANALYSIS")
print("=" * 65)

# 1. Dataset overview
print("\n1. DATASET OVERVIEW")
print(df.shape)
print(df.describe(include="all").T)

# 2. Target distribution
print("\n2. TARGET DISTRIBUTION")
print(df["target_low_score"].value_counts())

plt.figure(figsize=(7, 5))
sns.countplot(data=df, x="target_low_score")
plt.title("Next Assessment Risk Class Distribution")
plt.xlabel("Low score in next assessment (1 = Yes)")
plt.ylabel("Number of records")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "target_distribution.png", dpi=150)
plt.close()

# 3. Risk rate by assessment type
risk_by_type = (
    df.groupby("target_assessment_type")["target_low_score"]
    .mean()
    .mul(100)
    .reset_index(name="risk_percentage")
)

print("\n3. RISK RATE BY ASSESSMENT TYPE")
print(risk_by_type)

plt.figure(figsize=(7, 5))
sns.barplot(
    data=risk_by_type,
    x="target_assessment_type",
    y="risk_percentage"
)
plt.title("Low-Score Rate by Assessment Type")
plt.xlabel("Assessment type")
plt.ylabel("Low-score rate (%)")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "risk_by_assessment_type.png", dpi=150)
plt.close()

# 4. Historical mean score vs target
plt.figure(figsize=(8, 5))
sns.histplot(
    data=df,
    x="previous_mean_score",
    hue="target_low_score",
    bins=30,
    stat="density",
    common_norm=False,
    element="step"
)
plt.title("Historical Mean Score vs Next Assessment Risk")
plt.xlabel("Previous mean score")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "previous_mean_score.png", dpi=150)
plt.close()

# 5. Latest score vs target
plt.figure(figsize=(8, 5))
sns.boxplot(
    data=df,
    x="target_low_score",
    y="previous_latest_score"
)
plt.title("Previous Latest Score by Next Assessment Outcome")
plt.xlabel("Low score in next assessment (1 = Yes)")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "previous_latest_score.png", dpi=150)
plt.close()

# 6. VLE engagement distribution
print("\n6. ENGAGEMENT STATISTICS")
print(
    df[["total_clicks", "activity_records"]]
    .describe(percentiles=[0.25, 0.50, 0.75, 0.95, 0.99])
)

plt.figure(figsize=(8, 5))
sns.histplot(
    data=df,
    x="total_clicks",
    bins=50
)
plt.title("VLE Click Distribution Before Prediction")
plt.xlabel("Total clicks")
plt.xscale("symlog")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "vle_click_distribution.png", dpi=150)
plt.close()

# 7. Correlation analysis
numeric_columns = [
    "previous_scored_assessments",
    "previous_mean_score",
    "previous_latest_score",
    "total_clicks",
    "activity_records",
    "target_low_score"
]

correlation = df[numeric_columns].corr()

print("\n7. FEATURE CORRELATIONS")
print(correlation.round(3))

plt.figure(figsize=(9, 7))
sns.heatmap(
    correlation,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0
)
plt.title("Feature Correlation Matrix")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "correlation_matrix.png", dpi=150)
plt.close()

print("\nSaved EDA charts to:", FIGURE_DIR)

print("\n" + "=" * 65)
print("          EDA COMPLETED")
print("=" * 65)
