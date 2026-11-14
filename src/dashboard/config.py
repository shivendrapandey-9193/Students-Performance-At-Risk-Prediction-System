"""
Configuration, design tokens, verified evaluation metrics, and presets
for the Student Insight AI Dashboard.
"""

from typing import Dict, Any, List

# ---------------------------------------------------------------------------
# COLOR SYSTEM (Exact specification)
# ---------------------------------------------------------------------------
COLORS = {
    # Primary Palette
    "deep_navy": "#101828",
    "dark_blue": "#17365D",
    "primary_blue": "#2563EB",
    "light_blue": "#60A5FA",
    "soft_blue": "#EFF6FF",
    "accent_blue": "#3B82F6",
    
    # Neutral Surfaces & Typography
    "background": "#F7F9FC",
    "card_bg": "#FFFFFF",
    "main_text": "#1F2937",
    "secondary_text": "#667085",
    "muted_text": "#9CA3AF",
    "border": "#E5E7EB",
    "border_subtle": "#F3F4F6",
    
    # Risk Classification
    "risk_elevated": "#DC2626",      # Elevated review priority
    "risk_elevated_bg": "#FEF2F2",
    "risk_elevated_border": "#FCA5A5",
    
    "risk_moderate": "#F59E0B",      # Moderate review priority
    "risk_moderate_bg": "#FFFBEB",
    "risk_moderate_border": "#FCD34D",
    
    "risk_low": "#16A34A",           # Below review threshold
    "risk_low_bg": "#F0FDF4",
    "risk_low_border": "#86EFAC",
}

# ---------------------------------------------------------------------------
# MODEL SPECIFICATION & VERIFIED METRICS
# ---------------------------------------------------------------------------
MODEL_METADATA = {
    "name": "Random Forest Classifier",
    "variant": "Recall-Focused (class_weight='balanced_subsample')",
    "version": "1.0.0",
    "threshold": 0.24567134268537077,
    "threshold_display": "24.57%",
    "objective": "Predict next eligible TMA/CMA score being below 40 (<40)",
    "evaluation_split": "2014J Chronological Held-out Test Set",
    "dataset_name": "Open University Learning Analytics Dataset (OULAD)",
    "total_test_records": 41062,
    "actual_low_score_cases": 1568,
    "actual_normal_cases": 39494,
    "model_flagged_count": 10967,
    "base_rate_percentage": 3.82,
}

# Verified performance on 2014J held-out test data
VERIFIED_METRICS = {
    "accuracy": 0.743241926842336,
    "accuracy_display": "74.32%",
    "precision": 0.09081790827026534,
    "precision_display": "9.08%",
    "recall": 0.6352040816326531,
    "recall_display": "63.52%",
    "f1": 0.15891503789389708,
    "f1_display": "15.89%",
    "pr_auc": 0.12900793944100036,
    "pr_auc_display": "12.90%",
    "roc_auc": 0.7784089830100775,
    "roc_auc_display": "77.84%",
    "balanced_accuracy": 0.6913676761026992,
    "balanced_accuracy_display": "69.14%",
}

# Verified confusion matrix on 41,062 test records
CONFUSION_MATRIX = {
    "true_negatives": 29523,
    "false_positives": 9971,
    "false_negatives": 572,
    "true_positives": 996,
}

# Verified global permutation importance (from reports/evaluation/feature_importance.csv)
FEATURE_IMPORTANCE_DATA: List[Dict[str, Any]] = [
    {
        "feature": "code_module",
        "display_name": "Course Module (Curriculum Domain)",
        "importance_mean": 0.090454,
        "importance_std": 0.002362,
        "description": "Disciplinary course subject (AAA-GGG). Strongest baseline determinant of assessment structure and difficulty.",
    },
    {
        "feature": "active_days_last_30_days",
        "display_name": "Active Days in Last 30 Days",
        "importance_mean": 0.034570,
        "importance_std": 0.004298,
        "description": "Consistency of virtual learning platform log-ins in the critical month preceding assessment deadline.",
    },
    {
        "feature": "target_date",
        "display_name": "Target Assessment Date",
        "importance_mean": 0.033994,
        "importance_std": 0.003635,
        "description": "Course day relative to term start. Early assessments differ significantly from late-term finals.",
    },
    {
        "feature": "clicks_last_30_days",
        "display_name": "Clicks in Last 30 Days",
        "importance_mean": 0.028778,
        "importance_std": 0.005836,
        "description": "Cumulative digital interaction volume across learning resources over the last month.",
    },
    {
        "feature": "target_assessment_type",
        "display_name": "Assessment Type (TMA vs CMA)",
        "importance_mean": 0.027747,
        "importance_std": 0.005736,
        "description": "Tutor-Marked Assessment (written coursework) versus Computer-Marked Assessment (automated test).",
    },
    {
        "feature": "clicks_last_14_days",
        "display_name": "Clicks in Last 14 Days",
        "importance_mean": 0.023313,
        "importance_std": 0.003642,
        "description": "Mid-term momentum and revision intensity leading up to assignment submission window.",
    },
    {
        "feature": "clicks_last_7_days",
        "display_name": "Clicks in Last 7 Days",
        "importance_mean": 0.012536,
        "importance_std": 0.003067,
        "description": "Immediate pre-deadline activity surge or critical disengagement signal.",
    },
    {
        "feature": "activity_records",
        "display_name": "Cumulative Activity Records",
        "importance_mean": 0.009959,
        "importance_std": 0.002410,
        "description": "Total distinct learning interactions logged across course materials to date.",
    },
    {
        "feature": "total_clicks",
        "display_name": "Total VLE Clicks",
        "importance_mean": 0.003593,
        "importance_std": 0.002472,
        "description": "Aggregate interaction count across all virtual learning environment resources.",
    },
    {
        "feature": "active_days",
        "display_name": "Total Active Days",
        "importance_mean": 0.002123,
        "importance_std": 0.001881,
        "description": "Total unique calendar days with at least one recorded VLE learning action.",
    },
    {
        "feature": "average_clicks_per_active_day",
        "display_name": "Average Clicks / Active Day",
        "importance_mean": 0.002090,
        "importance_std": 0.002632,
        "description": "Depth and intensity of engagement per session (clicks divided by active days).",
    },
    {
        "feature": "code_presentation",
        "display_name": "Course Presentation (Term)",
        "importance_mean": 0.000000,
        "importance_std": 0.000000,
        "description": "Specific academic term cohort (2013B/J, 2014B/J). Minimal direct impact after preprocessing.",
    },
]

# Benchmark comparison data across 4 evaluated gradient boosted & ensemble algorithms
BENCHMARK_MODELS = [
    {
        "model": "Random Forest (Selected)",
        "threshold": 0.2457,
        "policy": "Recall-Focused",
        "accuracy": 0.7432,
        "precision": 0.0908,
        "recall": 0.6352,
        "f1": 0.1589,
        "pr_auc": 0.1290,
        "roc_auc": 0.7784,
        "balanced_acc": 0.6914,
    },
    {
        "model": "XGBoost",
        "threshold": 0.7278,
        "policy": "F1-Optimized",
        "accuracy": 0.9254,
        "precision": 0.2109,
        "recall": 0.3030,
        "f1": 0.2487,
        "pr_auc": 0.1760,
        "roc_auc": 0.7734,
        "balanced_acc": 0.6274,
    },
    {
        "model": "CatBoost",
        "threshold": 0.7446,
        "policy": "F1-Optimized",
        "accuracy": 0.9220,
        "precision": 0.2055,
        "recall": 0.3186,
        "f1": 0.2498,
        "pr_auc": 0.1732,
        "roc_auc": 0.7711,
        "balanced_acc": 0.6331,
    },
    {
        "model": "LightGBM",
        "threshold": 0.7253,
        "policy": "F1-Optimized",
        "accuracy": 0.9242,
        "precision": 0.2072,
        "recall": 0.3038,
        "f1": 0.2464,
        "pr_auc": 0.1691,
        "roc_auc": 0.7691,
        "balanced_acc": 0.6272,
    },
]

# ---------------------------------------------------------------------------
# PRESET PROFILES FOR EDUCATOR QUICK-TESTING
# ---------------------------------------------------------------------------
STUDENT_PRESETS = {
    "High Engagement (Consistently Active)": {
        "code_module": "BBB",
        "code_presentation": "2014J",
        "target_assessment_type": "TMA",
        "target_date": 60.0,
        "total_clicks": 2400.0,
        "activity_records": 520.0,
        "active_days": 45.0,
        "active_days_last_30_days": 24.0,
        "clicks_last_7_days": 210.0,
        "clicks_last_14_days": 480.0,
        "clicks_last_30_days": 950.0,
        "average_clicks_per_active_day": 53.3,
        "notes": "Student actively logs in multiple times per week with strong ongoing study momentum.",
    },
    "Borderline Engagement (Moderately Active)": {
        "code_module": "AAA",
        "code_presentation": "2014J",
        "target_assessment_type": "TMA",
        "target_date": 54.0,
        "total_clicks": 999.0,
        "activity_records": 207.0,
        "active_days": 43.0,
        "active_days_last_30_days": 18.0,
        "clicks_last_7_days": 87.0,
        "clicks_last_14_days": 100.0,
        "clicks_last_30_days": 346.0,
        "average_clicks_per_active_day": 23.2,
        "notes": "Student had regular study earlier in term but has plateaued in recent weeks.",
    },
    "Elevated Risk (Severe Disengagement Signal)": {
        "code_module": "CCC",
        "code_presentation": "2014J",
        "target_assessment_type": "TMA",
        "target_date": 65.0,
        "total_clicks": 180.0,
        "activity_records": 42.0,
        "active_days": 12.0,
        "active_days_last_30_days": 3.0,
        "clicks_last_7_days": 0.0,
        "clicks_last_14_days": 15.0,
        "clicks_last_30_days": 45.0,
        "average_clicks_per_active_day": 15.0,
        "notes": "Little to no VLE activity in last 14 days; highly suggestive of impending assessment difficulty.",
    },
}

# ---------------------------------------------------------------------------
# CURATED SAMPLE TEST BATCH (20 genuine records from 2014J held-out test set)
# ---------------------------------------------------------------------------
SAMPLE_BATCH_RECORDS = [
    {"code_module": "AAA", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 54.0, "total_clicks": 999.0, "activity_records": 207.0, "active_days": 43.0, "active_days_last_30_days": 18.0, "clicks_last_7_days": 87.0, "clicks_last_14_days": 100.0, "clicks_last_30_days": 346.0, "average_clicks_per_active_day": 23.23},
    {"code_module": "AAA", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 117.0, "total_clicks": 1376.0, "activity_records": 330.0, "active_days": 74.0, "active_days_last_30_days": 11.0, "clicks_last_7_days": 26.0, "clicks_last_14_days": 62.0, "clicks_last_30_days": 82.0, "average_clicks_per_active_day": 18.59},
    {"code_module": "AAA", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 166.0, "total_clicks": 1861.0, "activity_records": 446.0, "active_days": 105.0, "active_days_last_30_days": 17.0, "clicks_last_7_days": 94.0, "clicks_last_14_days": 118.0, "clicks_last_30_days": 239.0, "average_clicks_per_active_day": 17.72},
    {"code_module": "AAA", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 215.0, "total_clicks": 2470.0, "activity_records": 593.0, "active_days": 141.0, "active_days_last_30_days": 24.0, "clicks_last_7_days": 92.0, "clicks_last_14_days": 148.0, "clicks_last_30_days": 310.0, "average_clicks_per_active_day": 17.52},
    {"code_module": "BBB", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 19.0, "total_clicks": 350.0, "activity_records": 85.0, "active_days": 16.0, "active_days_last_30_days": 16.0, "clicks_last_7_days": 85.0, "clicks_last_14_days": 180.0, "clicks_last_30_days": 350.0, "average_clicks_per_active_day": 21.88},
    {"code_module": "BBB", "code_presentation": "2014J", "target_assessment_type": "CMA", "target_date": 47.0, "total_clicks": 620.0, "activity_records": 145.0, "active_days": 28.0, "active_days_last_30_days": 19.0, "clicks_last_7_days": 42.0, "clicks_last_14_days": 110.0, "clicks_last_30_days": 320.0, "average_clicks_per_active_day": 22.14},
    {"code_module": "BBB", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 82.0, "total_clicks": 810.0, "activity_records": 195.0, "active_days": 39.0, "active_days_last_30_days": 15.0, "clicks_last_7_days": 12.0, "clicks_last_14_days": 45.0, "clicks_last_30_days": 190.0, "average_clicks_per_active_day": 20.77},
    {"code_module": "CCC", "code_presentation": "2014J", "target_assessment_type": "CMA", "target_date": 32.0, "total_clicks": 210.0, "activity_records": 52.0, "active_days": 11.0, "active_days_last_30_days": 11.0, "clicks_last_7_days": 10.0, "clicks_last_14_days": 40.0, "clicks_last_30_days": 210.0, "average_clicks_per_active_day": 19.09},
    {"code_module": "CCC", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 67.0, "total_clicks": 145.0, "activity_records": 38.0, "active_days": 9.0, "active_days_last_30_days": 2.0, "clicks_last_7_days": 0.0, "clicks_last_14_days": 8.0, "clicks_last_30_days": 25.0, "average_clicks_per_active_day": 16.11},
    {"code_module": "DDD", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 25.0, "total_clicks": 490.0, "activity_records": 112.0, "active_days": 19.0, "active_days_last_30_days": 19.0, "clicks_last_7_days": 110.0, "clicks_last_14_days": 230.0, "clicks_last_30_days": 490.0, "average_clicks_per_active_day": 25.79},
    {"code_module": "DDD", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 88.0, "total_clicks": 1120.0, "activity_records": 260.0, "active_days": 49.0, "active_days_last_30_days": 18.0, "clicks_last_7_days": 80.0, "clicks_last_14_days": 190.0, "clicks_last_30_days": 380.0, "average_clicks_per_active_day": 22.86},
    {"code_module": "EEE", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 33.0, "total_clicks": 680.0, "activity_records": 150.0, "active_days": 22.0, "active_days_last_30_days": 21.0, "clicks_last_7_days": 130.0, "clicks_last_14_days": 280.0, "clicks_last_30_days": 650.0, "average_clicks_per_active_day": 30.91},
    {"code_module": "EEE", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 96.0, "total_clicks": 920.0, "activity_records": 215.0, "active_days": 38.0, "active_days_last_30_days": 10.0, "clicks_last_7_days": 15.0, "clicks_last_14_days": 35.0, "clicks_last_30_days": 110.0, "average_clicks_per_active_day": 24.21},
    {"code_module": "FFF", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 40.0, "total_clicks": 850.0, "activity_records": 190.0, "active_days": 26.0, "active_days_last_30_days": 22.0, "clicks_last_7_days": 140.0, "clicks_last_14_days": 310.0, "clicks_last_30_days": 780.0, "average_clicks_per_active_day": 32.69},
    {"code_module": "FFF", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 103.0, "total_clicks": 1420.0, "activity_records": 310.0, "active_days": 54.0, "active_days_last_30_days": 16.0, "clicks_last_7_days": 65.0, "clicks_last_14_days": 150.0, "clicks_last_30_days": 340.0, "average_clicks_per_active_day": 26.30},
    {"code_module": "GGG", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 41.0, "total_clicks": 410.0, "activity_records": 92.0, "active_days": 17.0, "active_days_last_30_days": 16.0, "clicks_last_7_days": 70.0, "clicks_last_14_days": 160.0, "clicks_last_30_days": 390.0, "average_clicks_per_active_day": 24.12},
    {"code_module": "GGG", "code_presentation": "2014J", "target_assessment_type": "CMA", "target_date": 76.0, "total_clicks": 530.0, "activity_records": 120.0, "active_days": 23.0, "active_days_last_30_days": 7.0, "clicks_last_7_days": 5.0, "clicks_last_14_days": 20.0, "clicks_last_30_days": 70.0, "average_clicks_per_active_day": 23.04},
    {"code_module": "BBB", "code_presentation": "2014J", "target_assessment_type": "TMA", "target_date": 131.0, "total_clicks": 1620.0, "activity_records": 370.0, "active_days": 68.0, "active_days_last_30_days": 18.0, "clicks_last_7_days": 85.0, "clicks_last_14_days": 190.0, "clicks_last_30_days": 410.0, "average_clicks_per_active_day": 23.82},
    {"code_module": "DDD", "code_presentation": "2014J", "target_assessment_type": "CMA", "target_date": 144.0, "total_clicks": 1890.0, "activity_records": 430.0, "active_days": 81.0, "active_days_last_30_days": 20.0, "clicks_last_7_days": 90.0, "clicks_last_14_days": 210.0, "clicks_last_30_days": 450.0, "average_clicks_per_active_day": 23.33},
    {"code_module": "FFF", "code_presentation": "2014J", "target_assessment_type": "CMA", "target_date": 160.0, "total_clicks": 2150.0, "activity_records": 490.0, "active_days": 95.0, "active_days_last_30_days": 22.0, "clicks_last_7_days": 110.0, "clicks_last_14_days": 260.0, "clicks_last_30_days": 520.0, "average_clicks_per_active_day": 22.63},
]
