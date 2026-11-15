/**
 * Comprehensive Knowledge Base for Insight AI Assistant
 * Provides verified project context, metrics, architecture, ML rationale,
 * interview Q&As, and ethical guidelines.
 */

const PROJECT_KNOWLEDGE_BASE = {
  project_overview: {
    name: "Student Insight AI — Academic Analytics & Early-Warning Platform",
    mission: "Empower academic advisors and course instructors to identify students at risk of assessment failure early in the semester, enabling proactive pedagogical interventions before assessments are submitted.",
    problem_statement: "Higher education distance learning suffers from high attrition and late failure detection. Standard university workflows only identify struggling students after they fail an exam. By leveraging Virtual Learning Environment (VLE) interaction logs prior to assessment cutoffs, Student Insight AI provides actionable early warnings.",
    advisory_nature: "Student Insight AI is strictly an early-warning advisory decision-support tool. It never automates grading, penalties, or academic sanctions. Predictions must be verified by educators who understand qualitative student circumstances."
  },

  system_architecture: {
    frontend: "React.js (v18+) single-page application built with Vite, styled with Tailwind CSS, Lucide React icons, and Recharts interactive visualizations. Seamless dual layout: public SaaS welcome/landing page at '/' and authenticated operational dashboard at '/app'.",
    backend: "Node.js (v20+) with Express.js REST API providing secure API routing, CSV batch processing with Multer, data validation, and streaming LLM integration with Groq.",
    ml_microservice: "Python FastAPI service hosting a Scikit-Learn Random Forest pipeline, containerized and deployed on Render with local development fallback (http://127.0.0.1:8000 and https://students-performance-at-risk-prediction.onrender.com).",
    ai_assistant: "Groq Cloud API utilizing high-throughput open-weight models (Qwen-2.5 32B / Llama 3) with an embedded domain knowledge base and conversational history."
  },

  dataset_and_split: {
    dataset_name: "Open University Learning Analytics Dataset (OULAD)",
    population: "32,593 students across 22 module presentations spanning STEM and Social Sciences courses.",
    target_definition: "Binary indicator: 1 if student's upcoming TMA (Tutor-Marked Assessment) or CMA (Computer-Marked Assessment) score is strictly below 40 points (<40 out of 100), 0 otherwise.",
    target_base_rate: "Severe class imbalance: approximately 3.8% positive (at-risk) across the entire dataset.",
    chronological_split: {
      rationale: "Random k-fold cross-validation or random train-test splitting introduces catastrophic future temporal leakage in academic time-series. A model trained on later semester data cannot realistically be tested on earlier students.",
      train_split: "2013B and 2013J academic presentations (15,907 student-assessment records) used exclusively for model fitting.",
      validation_split: "2014B academic presentation (31,171 student-assessment records) used strictly for hyperparameter tuning and optimal decision threshold selection.",
      test_split: "2014J academic presentation (41,062 student-assessment records) kept strictly blind and evaluated once for unbiased production assessment."
    }
  },

  champion_model_metrics: {
    algorithm: "Random Forest Classifier (Scikit-Learn)",
    hyperparameters: {
      n_estimators: 100,
      max_depth: 10,
      min_samples_split: 10,
      class_weight: "balanced_subsample",
      random_state: 42
    },
    decision_threshold: 0.24567134268537077,
    threshold_selection_rationale: "Selected on the 2014B validation set to achieve at least 60% operational recall. At the standard 0.50 cutoff, the model detects fewer than 25% of failing students due to the 3.8% base rate.",
    verified_test_metrics_2014J: {
      dataset_size: 41062,
      actual_positive_cases: 1568,
      flagged_students: 10967,
      accuracy: 0.7432,
      accuracy_display: "74.32%",
      recall: 0.6352,
      recall_display: "63.52%",
      precision: 0.0908,
      precision_display: "9.08%",
      f1_score: 0.1589,
      f1_display: "15.89%",
      roc_auc: 0.7784,
      roc_auc_display: "77.84%",
      pr_auc: 0.1290,
      pr_auc_display: "12.90%",
      balanced_accuracy: 0.6914,
      balanced_accuracy_display: "69.14%",
      confusion_matrix: {
        true_negatives: 29523,
        false_positives: 9971,
        false_negatives: 572,
        true_positives: 996
      }
    }
  },

  why_not_90_percent_accuracy: `
In heavily imbalanced domains (3.8% positive class), raw Accuracy is a misleading vanity metric:
1. A trivial dummy model predicting "safe (0)" for 100% of students achieves 96.2% accuracy but 0.0% recall, identifying ZERO at-risk students and offering zero pedagogical value.
2. We benchmarked LightGBM tuned for pure accuracy: it reached 90.88% accuracy, but recall collapsed to 30.93% (missing 1,083 out of 1,568 struggling students).
3. In student retention, False Negatives (a failing student who receives no help) are catastrophic, whereas False Positives (a passing student who receives a friendly check-in) carry minimal cost.
4. Hence, our decision threshold (0.2457) deliberately optimizes for 63.52% Recall and 77.84% ROC-AUC over deceptive 90%+ accuracy.
  `,

  features: [
    { name: "code_module", type: "Categorical", importance: "9.05%", description: "Curriculum code (AAA to GGG). Course discipline strongly modulates student interaction patterns." },
    { name: "active_days_last_30_days", type: "Continuous", importance: "3.46%", description: "Number of calendar days student logged in during the 30 days prior to submission." },
    { name: "target_date", type: "Continuous", importance: "3.40%", description: "Assessment deadline relative to term launch (day offset)." },
    { name: "clicks_last_30_days", type: "Continuous", importance: "2.88%", description: "Total VLE clickstream volume generated in the 30 days prior to assessment cutoff." },
    { name: "target_assessment_type", type: "Categorical", importance: "2.77%", description: "Type of evaluation: Tutor-Marked (TMA) vs Computer-Marked (CMA)." },
    { name: "clicks_last_14_days", type: "Continuous", importance: "2.33%", description: "Engagement volume in the critical 2-week pre-submission preparation window." },
    { name: "clicks_last_7_days", type: "Continuous", importance: "1.25%", description: "Engagement volume in the final 7 days before submission." },
    { name: "activity_records", type: "Continuous", importance: "1.00%", description: "Unique learning resource interaction records across forum, quiz, and content modules." },
    { name: "total_clicks", type: "Continuous", importance: "0.36%", description: "Cumulative click interactions across the entire semester to date." },
    { name: "active_days", type: "Continuous", importance: "0.21%", description: "Total distinct days the student has accessed course materials since course inception." },
    { name: "average_clicks_per_active_day", type: "Continuous", importance: "0.21%", description: "Study session intensity (total clicks divided by active days)." },
    { name: "code_presentation", type: "Categorical", importance: "0.00%", description: "Cohort presentation identifier (e.g., 2013B, 2014J)." }
  ],

  ethical_principles: [
    "Strictly Non-Punitive: Early warning flags can never be used to penalize, disenroll, or restrict student course access.",
    "Exclusion of Demographic Attributes: Protected demographics (gender, age band, disability, IMD index of multiple deprivation) are excluded from the core prediction features to prevent algorithmic bias and discriminatory profiling.",
    "Human-in-the-Loop: An advisor or professor must always review the student's broader context before reaching out.",
    "Data Minimization: Only aggregate interaction counts and timestamps are used; private communications and personal notes are never ingested."
  ]
};

module.exports = { PROJECT_KNOWLEDGE_BASE };
