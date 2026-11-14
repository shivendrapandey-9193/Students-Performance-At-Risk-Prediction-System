from pathlib import Path

root = Path(__file__).resolve().parent

api_path = root / "src/api/app.py"
dashboard_path = root / "src/dashboard/app.py"

def replace_once(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one match, found {count}. "
            "No safe automatic replacement was made."
        )
    return content.replace(old, new, 1)

# ---------------- API ----------------

api = api_path.read_text(encoding="utf-8")

api = replace_once(
    api,
    'MODEL_FILE = ROOT / "models" / "saved" / "random_forest.joblib"',
    'MODEL_FILE = ROOT / "models" / "candidates" / "random_forest.joblib"',
    "API model path",
)

api = replace_once(
    api,
    "THRESHOLD = 0.4583",
    "THRESHOLD = 0.24567134268537077",
    "API threshold",
)

api = replace_once(
    api,
    '"model": "Random Forest - Conservative",',
    '"model": "Random Forest - Recall Focused",',
    "API home model name",
)

api = replace_once(
    api,
    '"threshold": THRESHOLD,\n    }',
    '"threshold": THRESHOLD,\n        "model_file": str(MODEL_FILE.name),\n        "decision_policy": "Recall-focused; human review required",\n    }',
    "API home threshold metadata",
)

api = replace_once(
    api,
    '"model_loaded": model is not None,\n    }',
    '"model_loaded": model is not None,\n        "model": "Random Forest - Recall Focused",\n        "threshold": THRESHOLD,\n    }',
    "API health metadata",
)

api = replace_once(
    api,
    '"flagged_for_review": flagged,',
    '"flagged_for_review": flagged,\n            "risk_band": "Review recommended" if flagged else "Below review threshold",\n            "decision_policy": "Recall-focused threshold selected on validation data",',
    "API prediction metadata",
)

api_path.write_text(api, encoding="utf-8")

# ---------------- DASHBOARD ----------------

dashboard = dashboard_path.read_text(encoding="utf-8")

dashboard_replacements = [
    (
        "MODEL_THRESHOLD = 0.4583",
        "MODEL_THRESHOLD = 0.24567134268537077",
        "Dashboard threshold",
    ),
    (
        'metric_card("TEST ACCURACY", "88.14%", "Chronological test set")',
        'metric_card("TEST ACCURACY", "74.32%", "Chronological test set")',
        "Overview accuracy",
    ),
    (
        'metric_card("PRECISION", "13.70%", "Positive class")',
        'metric_card("PRECISION", "9.08%", "Positive class")',
        "Overview precision",
    ),
    (
        'metric_card("RECALL", "39.73%", "Positive class")',
        'metric_card("RECALL", "63.52%", "Positive class")',
        "Overview recall",
    ),
    (
        'metric_card("F1 SCORE", "20.37%", "Positive class")',
        'metric_card("F1 SCORE", "15.89%", "Positive class")',
        "Overview F1",
    ),
    (
        '                88.14,\n                13.70,\n                39.73,\n                20.37,\n                12.90,\n                77.84',
        '                74.32,\n                9.08,\n                63.52,\n                15.89,\n                12.90,\n                77.84',
        "Overview performance chart",
    ),
    (
        '                [35568, 3926],\n                [945, 623]',
        '                [29523, 9971],\n                [572, 996]',
        "Overview confusion matrix",
    ),
    (
        '"Test records: 41,062 | Threshold: 0.4583"',
        '"Test records: 41,062 | Threshold: 0.24567"',
        "Overview test caption",
    ),
    (
        '"The model has 13.70% precision on the chronological test set. "\n        "Many flagged records were not low-scoring. Predictions should "\n        "only support educator review, never automatic academic decisions."',
        '"At the recall-focused threshold, test precision is 9.08% and recall "\n        "is 63.52%. False-positive referrals are substantial. Predictions "\n        "must support educator review, never automatic academic decisions."',
        "Overview limitation",
    ),
    (
        '"Decision threshold: 0.4583, selected using validation data"',
        '"Decision threshold: 0.24567, selected using validation data"',
        "Model architecture threshold",
    ),
    (
        '"- Test precision is 13.70%, so false-positive alerts are substantial.\\n'
        '    - Test recall is 39.73%, so many low-score records are missed.\\n'
        '    - Course module is the strongest permutation-importance feature.\\n'
        '    - Feature importance is not evidence that a feature causes low scores.\\n'
        '    - Historical OULAD data does not provide exact grade-release timestamps."',
        '"- At this operating threshold, test precision is 9.08% and recall is 63.52%.\\n'
        '    - The model flagged 10,967 of 41,062 test records.\\n'
        '    - There were 9,971 false positives and 572 false negatives.\\n'
        '    - Course module is the strongest permutation-importance feature.\\n'
        '    - Feature importance is not evidence of causation.\\n'
        '    - Historical OULAD data does not provide exact grade-release timestamps."',
        "Model limitations",
    ),
]

for old, new, label in dashboard_replacements:
    dashboard = replace_once(dashboard, old, new, label)

dashboard_path.write_text(dashboard, encoding="utf-8")

print("Successfully updated FastAPI and Streamlit.")
print("API model: models/candidates/random_forest.joblib")
print("Decision threshold:", 0.24567134268537077)
print("Dashboard evaluation figures updated.")
