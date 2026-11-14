
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

API_URL = "http://127.0.0.1:8000"
MODEL_NAME = "Random Forest"
MODEL_THRESHOLD = 0.4583

st.set_page_config(
    page_title="Student Intelligence | AI Risk Analytics",
    page_icon="ðŸŽ“",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0b1120;
    color: #e5e7eb;
}

[data-testid="stSidebar"] {
    background: #111b2e;
    border-right: 1px solid #26344d;
}

[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

.main-title {
    font-size: 31px;
    font-weight: 800;
    color: #f8fafc;
    letter-spacing: -1px;
}

.subtitle {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 25px;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #f1f5f9;
    margin-top: 15px;
    margin-bottom: 15px;
}

.metric-card {
    background: linear-gradient(145deg, #17243a, #111b2e);
    border: 1px solid #293b57;
    border-radius: 14px;
    padding: 20px;
    min-height: 120px;
}

.metric-label {
    color: #94a3b8;
    font-size: 13px;
    font-weight: 500;
}

.metric-value {
    color: #f8fafc;
    font-size: 29px;
    font-weight: 800;
    margin-top: 8px;
}

.metric-caption {
    color: #94a3b8;
    font-size: 12px;
    margin-top: 5px;
}

.status-pill {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}

.flagged {
    color: #fecaca;
    background: #451a1a;
    border: 1px solid #7f1d1d;
}

.safe {
    color: #bbf7d0;
    background: #123322;
    border: 1px solid #166534;
}

.info-panel {
    background: #142238;
    border: 1px solid #293b57;
    border-radius: 12px;
    padding: 17px;
}

div.stButton > button[kind="primary"],
div.stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(90deg, #2563eb, #4f46e5);
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    min-height: 45px;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    border: 1px solid #60a5fa;
}

div[data-testid="stMetric"] {
    background: #142238;
    border: 1px solid #293b57;
    padding: 15px;
    border-radius: 12px;
}

[data-testid="stProgressBar"] > div > div {
    background-color: #3b82f6;
}

hr {
    border-color: #293b57;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

if "latest_prediction" not in st.session_state:
    st.session_state.latest_prediction = None

# --------------------------------------------------
# API CONNECTION
# --------------------------------------------------

def check_api():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        return bool(data.get("model_loaded")), data
    except requests.RequestException:
        return False, {}

api_connected, api_data = check_api()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## ðŸŽ“ STUDENT AI")
    st.caption("ACADEMIC INTELLIGENCE PLATFORM")

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Risk Prediction",
            "Model Insights",
            "Prediction History"
        ],
        label_visibility="visible"
    )

    st.divider()

    st.markdown("### SYSTEM STATUS")

    if api_connected:
        st.success("Prediction API Online")
        st.caption("Random Forest model loaded")
    else:
        st.error("Prediction API Offline")
        st.caption("Start your FastAPI backend.")

    st.divider()

    st.markdown("### MODEL INFORMATION")
    st.caption(f"Algorithm: {MODEL_NAME}")
    st.caption(f"Decision threshold: {MODEL_THRESHOLD:.2%}")
    st.caption("Target: Next assessment score below 40")

    st.divider()
    st.caption("Student At-Risk Prediction")
    st.caption("Advisory decision-support system")

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">Student Performance Intelligence</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI-powered academic risk monitoring and early intervention platform</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# REUSABLE METRIC CARD
# --------------------------------------------------

def metric_card(label, value, caption):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-caption">{caption}</div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if page == "Overview":

    st.markdown("### Platform Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("TEST ACCURACY", "88.14%", "Chronological test set")

    with col2:
        metric_card("PRECISION", "13.70%", "Positive class")

    with col3:
        metric_card("RECALL", "39.73%", "Positive class")

    with col4:
        metric_card("F1 SCORE", "20.37%", "Positive class")

    st.markdown("### Model Evaluation")

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("#### Test-set performance")

        performance = pd.DataFrame({
            "Metric": [
                "Accuracy",
                "Precision",
                "Recall",
                "F1 Score",
                "PR-AUC",
                "ROC-AUC"
            ],
            "Score": [
                88.14,
                13.70,
                39.73,
                20.37,
                12.90,
                77.84
            ]
        })

        st.dataframe(
            performance,
            width="stretch",
            hide_index=True,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Score (%)",
                    min_value=0,
                    max_value=100,
                    format="%.2f%%"
                )
            }
        )

    with right:
        st.markdown("#### Confusion matrix")

        confusion = pd.DataFrame(
            [
                [35568, 3926],
                [945, 623]
            ],
            index=["Actual normal", "Actual low score"],
            columns=["Predicted normal", "Predicted low score"]
        )

        st.dataframe(
            confusion,
            width="stretch"
        )

        st.caption(
            "Test records: 41,062 | Threshold: 0.4583"
        )

    st.markdown("### Dataset Overview")

    a, b, c = st.columns(3)

    with a:
        metric_card("TOTAL RECORDS", "141,946", "Candidate assessment records")

    with b:
        metric_card("UNIQUE STUDENTS", "21,246", "Across candidate records")

    with c:
        metric_card("LOW-SCORE RECORDS", "5,304", "3.74% of candidate records")

    st.markdown("### Important model limitation")

    st.warning(
        "The model has 13.70% precision on the chronological test set. "
        "Many flagged records were not low-scoring. Predictions should "
        "only support educator review, never automatic academic decisions."
    )

# --------------------------------------------------
# RISK PREDICTION PAGE
# --------------------------------------------------

elif page == "Risk Prediction":

    st.markdown("### Student Risk Assessment")

    st.markdown(
        '<div class="subtitle">Enter engagement information available before the target assessment.</div>',
        unsafe_allow_html=True
    )

    if not api_connected:
        st.error("Prediction API is unavailable. Start FastAPI before predicting.")
        st.stop()

    with st.form("advanced_prediction_form"):

        st.markdown("#### 01 â€” Assessment information")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            module = st.selectbox(
                "Course module",
                ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG"]
            )

        with c2:
            presentation = st.selectbox(
                "Presentation",
                ["2013B", "2013J", "2014B", "2014J"]
            )

        with c3:
            assessment_type = st.selectbox(
                "Assessment type",
                ["TMA", "CMA"]
            )

        with c4:
            target_date = st.number_input(
                "Days from course start",
                min_value=1,
                max_value=300,
                value=30
            )

        st.divider()
        st.markdown("#### 02 â€” Overall learning engagement")

        c1, c2, c3 = st.columns(3)

        with c1:
            total_clicks = st.number_input(
                "Total VLE clicks",
                min_value=0,
                value=1000
            )

        with c2:
            activity_records = st.number_input(
                "Activity records",
                min_value=0,
                value=300
            )

        with c3:
            active_days = st.number_input(
                "Total active days",
                min_value=0,
                value=40
            )

        st.divider()
        st.markdown("#### 03 â€” Recent engagement")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            active_days_last_30_days = st.number_input(
                "Active days (30 days)",
                min_value=0,
                max_value=30,
                value=10
            )

        with c2:
            clicks_last_7_days = st.number_input(
                "Clicks (7 days)",
                min_value=0,
                value=100
            )

        with c3:
            clicks_last_14_days = st.number_input(
                "Clicks (14 days)",
                min_value=0,
                value=250
            )

        with c4:
            clicks_last_30_days = st.number_input(
                "Clicks (30 days)",
                min_value=0,
                value=500
            )

        average_clicks_per_active_day = st.number_input(
            "Average clicks per active day",
            min_value=0.0,
            value=25.0,
            step=0.5
        )

        st.divider()

        submitted = st.form_submit_button(
            "âš¡ ANALYZE STUDENT RISK",
            type="primary",
            width="stretch"
        )

    if submitted:

        errors = []

        if not (
            clicks_last_7_days
            <= clicks_last_14_days
            <= clicks_last_30_days
            <= total_clicks
        ):
            errors.append(
                "Clicks must follow: 7 days â‰¤ 14 days â‰¤ 30 days â‰¤ total clicks."
            )

        if active_days_last_30_days > active_days:
            errors.append(
                "Recent active days cannot exceed total active days."
            )

        if errors:
            for error in errors:
                st.error(error)

        else:

            payload = {
                "code_module": module,
                "code_presentation": presentation,
                "target_assessment_type": assessment_type,
                "target_date": int(target_date),
                "total_clicks": int(total_clicks),
                "activity_records": int(activity_records),
                "active_days": int(active_days),
                "active_days_last_30_days": int(active_days_last_30_days),
                "clicks_last_7_days": int(clicks_last_7_days),
                "clicks_last_14_days": int(clicks_last_14_days),
                "clicks_last_30_days": int(clicks_last_30_days),
                "average_clicks_per_active_day": float(
                    average_clicks_per_active_day
                )
            }

            try:
                with st.spinner("Analyzing student engagement..."):

                    response = requests.post(
                        f"{API_URL}/predict",
                        json=payload,
                        timeout=30
                    )

                if response.status_code == 200:

                    result = response.json()

                    probability = float(result["predicted_probability"])
                    threshold = float(result["threshold"])
                    flagged = bool(result["flagged_for_review"])

                    record = {
                        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Module": module,
                        "Presentation": presentation,
                        "Assessment": assessment_type,
                        "Probability": probability,
                        "Status": "Flagged" if flagged else "Not flagged"
                    }

                    st.session_state.latest_prediction = {
                        "result": result,
                        "record": record
                    }

                    st.session_state.prediction_history.insert(0, record)

                else:
                    st.error(
                        f"API error {response.status_code}: {response.text}"
                    )

            except requests.RequestException as error:
                st.error(f"Prediction request failed: {error}")

    # Display latest prediction outside the form
    latest = st.session_state.latest_prediction

    if latest:

        result = latest["result"]
        probability = float(result["predicted_probability"])
        threshold = float(result["threshold"])
        flagged = bool(result["flagged_for_review"])

        st.divider()
        st.markdown("### Prediction Report")

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "LOW-SCORE PROBABILITY",
                f"{probability:.2%}",
                "Model-predicted probability"
            )

        with c2:
            metric_card(
                "DECISION THRESHOLD",
                f"{threshold:.2%}",
                "Selected on validation data"
            )

        with c3:
            metric_card(
                "REVIEW STATUS",
                "FLAGGED" if flagged else "NOT FLAGGED",
                "Model decision at selected threshold"
            )

        st.markdown("#### Probability indicator")
        st.progress(max(0.0, min(1.0, probability)))

        if flagged:
            st.error(
                "âš ï¸ This record has been flagged for human review. "
                "An educator should assess whether additional academic "
                "support may be appropriate."
            )
        else:
            st.success(
                "This record was not flagged at the selected threshold. "
                "This does not guarantee a successful assessment outcome."
            )

        st.markdown("#### Model response")

        with st.expander("View complete prediction details"):
            st.json(result)

        st.info(
            "The prediction is an advisory signal, not a confirmed outcome. "
            "The dashboard does not establish why a student may be at risk."
        )

# --------------------------------------------------
# MODEL INSIGHTS PAGE
# --------------------------------------------------

elif page == "Model Insights":

    st.markdown("### Model Intelligence & Explainability")

    st.markdown(
        "The following are validation-set permutation importance results. "
        "They show how much predictive performance changes when a feature "
        "is shuffled; they do not establish causation."
    )

    importance = pd.DataFrame({
        "Feature": [
            "Course module",
            "Active days (last 30)",
            "Target assessment date",
            "Clicks (last 30 days)",
            "Assessment type",
            "Clicks (last 14 days)",
            "Clicks (last 7 days)",
            "Activity records",
            "Total clicks",
            "Total active days",
            "Average clicks per active day",
            "Course presentation"
        ],
        "Importance": [
            0.090454,
            0.034570,
            0.033994,
            0.028778,
            0.027747,
            0.023313,
            0.012536,
            0.009959,
            0.003593,
            0.002123,
            0.002090,
            0.000000
        ]
    })

    st.markdown("#### Feature importance")

    st.bar_chart(
        importance.set_index("Feature"),
        horizontal=True
    )

    st.markdown("#### Model architecture")

    st.markdown("""
    <div class="info-panel">
    <b>Algorithm:</b> Random Forest Classifier<br><br>
    <b>Training strategy:</b> Chronological presentation split<br><br>
    <b>Training presentations:</b> 2013B and 2013J<br><br>
    <b>Validation presentation:</b> 2014B<br><br>
    <b>Test presentation:</b> 2014J<br><br>
    <b>Class imbalance handling:</b> Balanced subsample class weights<br><br>
    <b>Decision threshold:</b> 0.4583, selected using validation data
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Important limitations")

    st.warning("""
    - Test precision is 13.70%, so false-positive alerts are substantial.
    - Test recall is 39.73%, so many low-score records are missed.
    - Course module is the strongest permutation-importance feature.
    - Feature importance is not evidence that a feature causes low scores.
    - Historical OULAD data does not provide exact grade-release timestamps.
    """)

# --------------------------------------------------
# PREDICTION HISTORY PAGE
# --------------------------------------------------

elif page == "Prediction History":

    st.markdown("### Prediction History")

    history = st.session_state.prediction_history

    if history:

        history_df = pd.DataFrame(history)

        total = len(history_df)
        flagged_count = int(
            (history_df["Status"] == "Flagged").sum()
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card("TOTAL PREDICTIONS", str(total), "Current session")

        with c2:
            metric_card("FLAGGED", str(flagged_count), "For educator review")

        with c3:
            metric_card(
                "NOT FLAGGED",
                str(total - flagged_count),
                "Below selected threshold"
            )

        st.markdown("#### Prediction records")

        st.dataframe(
            history_df,
            width="stretch",
            hide_index=True
        )

        csv = history_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "â¬‡ Download prediction history",
            data=csv,
            file_name="student_prediction_history.csv",
            mime="text/csv"
        )

        if st.button("Clear session history"):
            st.session_state.prediction_history = []
            st.session_state.latest_prediction = None
            st.rerun()

    else:
        st.info(
            "No predictions yet. Go to Risk Prediction to generate your first record."
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Student At-Risk Prediction | Random Forest + FastAPI + Streamlit | "
    "For academic support and human review only."
)


