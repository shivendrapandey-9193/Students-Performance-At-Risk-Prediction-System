/**
 * Verified Domain Knowledge for Student Insight AI
 */
export const PROJECT_KNOWLEDGE = {
  name: "Student Insight AI — Academic Analytics Platform",
  dataset: "Open University Learning Analytics Dataset (OULAD)",
  total_students: 32593,
  test_cohort_size: 41062,
  test_presentation: "2014J",
  model_name: "Random Forest Classifier",
  threshold: 0.24567134268537077,
  threshold_display: "0.2457",
  metrics: {
    accuracy: "74.32%",
    recall: "63.52%",
    precision: "9.08%",
    f1_score: "15.89%",
    roc_auc: "77.84%",
    pr_auc: "12.90%",
    balanced_accuracy: "69.14%",
    confusion_matrix: {
      tn: 29523,
      fp: 9971,
      fn: 572,
      tp: 996
    }
  },
  why_not_90_accuracy: "In this dataset, only ~3.8% of student assessment scores are below 40 (failing). A naive dummy model predicting 'safe' for 100% of students gets 96.2% accuracy but 0% recall, detecting ZERO at-risk students. We benchmarked LightGBM which achieved 90.88% accuracy, but recall collapsed to 30.93% (missing 1,083 failing students). Our calibrated Random Forest with threshold 0.2457 catches 63.52% of struggling students, prioritizing student retention over deceptive raw accuracy.",
  chronological_split: "Train: 2013B & 2013J (15,907). Validation: 2014B (31,171) for cutoff tuning. Test: 2014J (41,062). Enforces strict chronological order with zero future temporal leakage.",
  features: [
    "code_module (Course module AAA-GGG)",
    "active_days_last_30_days (Active login days in last 30d)",
    "target_date (Assessment submission deadline)",
    "clicks_last_30_days (Click volume in last 30d)",
    "target_assessment_type (TMA vs CMA)",
    "clicks_last_14_days (Click volume in last 14d)",
    "clicks_last_7_days (Click volume in last 7d)",
    "activity_records (Distinct interaction logs)",
    "total_clicks (Cumulative clicks to date)",
    "active_days (Total active days since course start)",
    "average_clicks_per_active_day (Engagement density)",
    "code_presentation (Term cohort identifier)"
  ]
};
