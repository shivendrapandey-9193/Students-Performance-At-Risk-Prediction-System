"""
Student Insight AI — Academic Analytics & Early At-Risk Decision Support Platform
Enterprise SaaS Dashboard built with Streamlit, Plotly, and FastAPI integration.
"""

from datetime import datetime
import io
import pandas as pd
import streamlit as st

from src.dashboard.config import (
    COLORS,
    MODEL_METADATA,
    VERIFIED_METRICS,
    CONFUSION_MATRIX,
    FEATURE_IMPORTANCE_DATA,
    BENCHMARK_MODELS,
    STUDENT_PRESETS,
    SAMPLE_BATCH_RECORDS,
)
from src.dashboard.api_client import (
    DEFAULT_API_URL,
    check_api_health,
    predict_student_risk,
    predict_batch_records,
)
from src.dashboard.ui_components import (
    inject_custom_css,
    render_html,
    render_top_header,
    render_sidebar_nav,
    render_kpi_card,
    render_policy_banner,
    render_confusion_matrix_chart,
    render_feature_importance_chart,
    render_benchmark_chart,
    render_probability_gauge,
    render_prediction_result_card,
    render_why_flagged_accordion,
)

# ---------------------------------------------------------------------------
# STREAMLIT CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Student Insight AI | Academic Intelligence Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom SaaS CSS tokens
inject_custom_css()

# ---------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------------------------
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

if "latest_prediction" not in st.session_state:
    st.session_state.latest_prediction = None

if "batch_results" not in st.session_state:
    st.session_state.batch_results = None

if "preset_selection" not in st.session_state:
    st.session_state.preset_selection = "High Engagement (Consistently Active)"

# ---------------------------------------------------------------------------
# REAL-TIME API HEALTH PING
# ---------------------------------------------------------------------------
api_health = check_api_health(DEFAULT_API_URL, timeout=2.5)
api_connected = api_health["connected"]
api_latency = api_health["latency_ms"]
active_threshold = api_health.get("threshold") or MODEL_METADATA["threshold"]

# Render Brand Sidebar Navigation
selected_page = render_sidebar_nav(api_connected, active_threshold)


# ===========================================================================
# PAGE 1: DASHBOARD (EXECUTIVE OVERVIEW)
# ===========================================================================
if selected_page == "Dashboard":
    refresh = render_top_header(
        title="Student Performance Intelligence",
        subtitle="Executive analytics and early alert indicators for upcoming academic assessments.",
        api_connected=api_connected,
        latency_ms=api_latency,
        model_name="Random Forest — Recall-Focused",
    )
    if refresh:
        st.rerun()

    # Model Policy Callout
    render_policy_banner(threshold=active_threshold)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("### Verified Model Evaluation Metrics")
    st.caption("Chronological held-out test evaluation on unseen future presentation 2014J (41,062 candidate records).")

    # 6 Verified KPI Cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        render_kpi_card(
            title="Accuracy",
            value=VERIFIED_METRICS["accuracy_display"],
            explanation="Overall test accuracy across 41,062 records.",
            tooltip="Proportion of all predictions that were correct (TN + TP) / Total.",
            border_accent=COLORS["primary_blue"],
        )
    with col2:
        render_kpi_card(
            title="Recall",
            value=VERIFIED_METRICS["recall_display"],
            explanation="Identifies 63.5% of true at-risk cases.",
            tooltip="True Positive Rate: TP / (TP + FN). Deliberately prioritized to catch struggling students.",
            border_accent=COLORS["risk_elevated"],
        )
    with col3:
        render_kpi_card(
            title="Precision",
            value=VERIFIED_METRICS["precision_display"],
            explanation="Reflects recall trade-off on imbalanced class.",
            tooltip="Positive Predictive Value: TP / (TP + FP). Lower precision produces false positives requiring educator triage.",
            border_accent=COLORS["risk_moderate"],
        )
    with col4:
        render_kpi_card(
            title="F1 Score",
            value=VERIFIED_METRICS["f1_display"],
            explanation="Harmonic mean of precision and recall.",
            tooltip="2 * (Precision * Recall) / (Precision + Recall).",
            border_accent="#8B5CF6",
        )
    with col5:
        render_kpi_card(
            title="ROC-AUC",
            value=VERIFIED_METRICS["roc_auc_display"],
            explanation="Discrimination ability across all thresholds.",
            tooltip="Area under the Receiver Operating Characteristic curve.",
            border_accent=COLORS["primary_blue"],
        )
    with col6:
        render_kpi_card(
            title="PR-AUC",
            value=VERIFIED_METRICS["pr_auc_display"],
            explanation="Precision-Recall Area on test split.",
            tooltip="Area Under the Precision-Recall Curve. Strong benchmark for imbalanced targets.",
            border_accent="#0D9488",
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Visualizations Row 1: Confusion Matrix & Recall Trade-off Narrative
    viz_col_left, viz_col_right = st.columns([1.25, 1])

    with viz_col_left:
        fig_cm = render_confusion_matrix_chart()
        st.plotly_chart(fig_cm, use_container_width=True)

    with viz_col_right:
        render_html(f"""
        <div class="saas-card" style="height: 340px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div class="card-title">Precision vs. Recall in Academic Screening</div>
                <div class="card-subtitle">Pedagogical rationale for operating at &tau; = {active_threshold:.4f}</div>
                <p style="font-size: 13px; color: {COLORS['main_text']}; line-height: 1.5; margin-bottom: 12px;">
                    In early alert educational systems, the <strong>pedagogical cost of a False Negative</strong> (failing to identify 
                    a struggling student who subsequently fails) is significantly higher than the <strong>triage cost of a False Positive</strong> 
                    (checking in with a student who is doing well).
                </p>
                <ul style="font-size: 12.5px; color: {COLORS['secondary_text']}; padding-left: 18px; margin-bottom: 10px; line-height: 1.45;">
                    <li><strong>Base Low-Score Rate:</strong> Only 3.82% of test records scored below 40.</li>
                    <li><strong>Recall Priority:</strong> Tuning the threshold down to ~24.57% successfully catches <strong>63.52% (996 students)</strong> of all low scores.</li>
                    <li><strong>Trade-Off:</strong> Produces 9,971 false positives (~10 flagged alerts for every 1 true positive).</li>
                </ul>
            </div>
            <div style="background: #F8FAFC; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 10px; font-size: 12px; color: {COLORS['dark_blue']}; font-weight: 500;">
                Policy Guideline: Flagged students should receive supportive outreach or check-in emails, never disciplinary action.
            </div>
        </div>
        """)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Visualizations Row 2: Model Benchmark & Target Distribution
    row2_left, row2_right = st.columns([1.1, 1.1])

    with row2_left:
        fig_bench = render_benchmark_chart(BENCHMARK_MODELS)
        st.plotly_chart(fig_bench, use_container_width=True)

    with row2_right:
        fig_fi = render_feature_importance_chart(FEATURE_IMPORTANCE_DATA)
        st.plotly_chart(fig_fi, use_container_width=True)

    # Target Class Distribution & Workload Analysis Card
    render_html(f"""
    <div class="saas-card">
        <div class="card-title">Test Set Distribution & Educator Workload Implications</div>
        <div class="card-subtitle">Real numbers from the held-out 2014J evaluation dataset (41,062 records)</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 14px;">
            <div style="background: #F8FAFC; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 12px;">
                <div style="font-size: 11px; font-weight: 600; color: {COLORS['secondary_text']}; text-transform: uppercase;">Total Test Records</div>
                <div style="font-size: 20px; font-weight: 800; color: {COLORS['deep_navy']};">41,062</div>
                <div style="font-size: 12px; color: {COLORS['secondary_text']};">100% of evaluation split</div>
            </div>
            <div style="background: #F8FAFC; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 12px;">
                <div style="font-size: 11px; font-weight: 600; color: {COLORS['secondary_text']}; text-transform: uppercase;">Actual Low Scores (&lt;40)</div>
                <div style="font-size: 20px; font-weight: 800; color: {COLORS['risk_elevated']};">1,568</div>
                <div style="font-size: 12px; color: {COLORS['secondary_text']};">3.82% base prevalence</div>
            </div>
            <div style="background: #F8FAFC; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 12px;">
                <div style="font-size: 11px; font-weight: 600; color: {COLORS['secondary_text']}; text-transform: uppercase;">Actual Normal Scores (&ge;40)</div>
                <div style="font-size: 20px; font-weight: 800; color: {COLORS['risk_low']};">39,494</div>
                <div style="font-size: 12px; color: {COLORS['secondary_text']};">96.18% passing rate</div>
            </div>
            <div style="background: #F8FAFC; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 12px;">
                <div style="font-size: 11px; font-weight: 600; color: {COLORS['secondary_text']}; text-transform: uppercase;">Total Flagged for Review</div>
                <div style="font-size: 20px; font-weight: 800; color: {COLORS['primary_blue']};">10,967</div>
                <div style="font-size: 12px; color: {COLORS['secondary_text']};">26.71% screening volume</div>
            </div>
        </div>
        <p style="font-size: 13px; color: {COLORS['secondary_text']}; margin: 0; line-height: 1.5;">
            <strong>Workload Management Recommendation:</strong> Because 26.71% of all student assessments are flagged to achieve ~64% recall, 
            academic departments should implement <em>multi-tiered intervention protocols</em>: automated check-in prompts or resource links 
            for general flags, reserving intensive one-on-one tutor outreach for students showing both low VLE activity and prior assessment challenges.
        </p>
    </div>
    """)


# ===========================================================================
# PAGE 2: STUDENT RISK ASSESSMENT (INTERACTIVE PREDICTION)
# ===========================================================================
elif selected_page == "Student Risk Assessment":
    refresh = render_top_header(
        title="Student Risk Assessment",
        subtitle="Evaluate individual student engagement signals ahead of target assessment deadlines.",
        api_connected=api_connected,
        latency_ms=api_latency,
        model_name="Random Forest — Recall-Focused",
    )
    if refresh:
        st.rerun()

    if not api_connected:
        st.error(
            "**FastAPI Prediction Backend Offline:** The interactive assessment tool requires a live connection to "
            "`http://127.0.0.1:8000`. Please start the backend service using the command in the **API Status** tab."
        )

    # Preset Profile Loader
    st.markdown("### 1. Quick Scenario Loader (Optional)")
    st.caption("Select a validated student profile to populate realistic inputs or enter values manually below.")

    preset_col1, preset_col2 = st.columns([2.5, 1])
    with preset_col1:
        chosen_preset = st.selectbox(
            "Select Preset Profile",
            list(STUDENT_PRESETS.keys()),
            index=0,
            label_visibility="collapsed",
        )
    with preset_col2:
        preset_notes = STUDENT_PRESETS[chosen_preset]["notes"]
        render_html(f"<div style='font-size: 12px; color: {COLORS['secondary_text']}; padding: 6px 0;'><em>{preset_notes}</em></div>")

    preset_data = STUDENT_PRESETS[chosen_preset]

    st.markdown("### 2. Student Engagement Information")

    with st.form("risk_assessment_form"):
        # Section A: Course & Assessment Context
        st.markdown("#### Section A — Course & Assessment Context")
        a1, a2, a3, a4 = st.columns(4)
        with a1:
            module = st.selectbox(
                "Course Module",
                ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG"],
                index=["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG"].index(preset_data["code_module"]),
                help="Domain subject code of the course module.",
            )
        with a2:
            presentation = st.selectbox(
                "Course Presentation",
                ["2013B", "2013J", "2014B", "2014J"],
                index=["2013B", "2013J", "2014B", "2014J"].index(preset_data["code_presentation"]),
                help="Academic term presentation cohort.",
            )
        with a3:
            assessment_type = st.selectbox(
                "Assessment Type",
                ["TMA", "CMA"],
                index=["TMA", "CMA"].index(preset_data["target_assessment_type"]),
                help="TMA = Tutor-Marked Assessment; CMA = Computer-Marked Assessment.",
            )
        with a4:
            target_date = st.number_input(
                "Assessment Due Date (Day)",
                min_value=1.0,
                max_value=300.0,
                value=float(preset_data["target_date"]),
                step=1.0,
                help="Days elapsed from official course start date.",
            )

        st.markdown("<hr style='border-color: #F1F5F9; margin: 16px 0;'>", unsafe_allow_html=True)

        # Section B: Cumulative Engagement Footprint
        st.markdown("#### Section B — Cumulative Learning Activity")
        b1, b2, b3 = st.columns(3)
        with b1:
            total_clicks = st.number_input(
                "Total VLE Clicks to Date",
                min_value=0.0,
                value=float(preset_data["total_clicks"]),
                step=10.0,
                help="Total digital interactions across all learning materials.",
            )
        with b2:
            activity_records = st.number_input(
                "Cumulative Activity Records",
                min_value=0.0,
                value=float(preset_data["activity_records"]),
                step=5.0,
                help="Total distinct interaction events logged in the VLE database.",
            )
        with b3:
            active_days = st.number_input(
                "Total Active Days",
                min_value=0.0,
                value=float(preset_data["active_days"]),
                step=1.0,
                help="Unique calendar dates with at least one recorded learning activity.",
            )

        st.markdown("<hr style='border-color: #F1F5F9; margin: 16px 0;'>", unsafe_allow_html=True)

        # Section C: Recent Activity Dynamics (Last 7, 14, 30 days)
        st.markdown("#### Section C — Recent Engagement Dynamics")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            active_days_last_30_days = st.number_input(
                "Active Days in Last 30 Days",
                min_value=0.0,
                max_value=30.0,
                value=float(preset_data["active_days_last_30_days"]),
                step=1.0,
                help="Number of days active in the month leading up to the assessment (max 30).",
            )
        with c2:
            clicks_last_7_days = st.number_input(
                "Clicks in Last 7 Days",
                min_value=0.0,
                value=float(preset_data["clicks_last_7_days"]),
                step=5.0,
                help="VLE interaction count in the final 7 days.",
            )
        with c3:
            clicks_last_14_days = st.number_input(
                "Clicks in Last 14 Days",
                min_value=0.0,
                value=float(preset_data["clicks_last_14_days"]),
                step=10.0,
                help="VLE interaction count in the last 14 days (must be >= 7 days clicks).",
            )
        with c4:
            clicks_last_30_days = st.number_input(
                "Clicks in Last 30 Days",
                min_value=0.0,
                value=float(preset_data["clicks_last_30_days"]),
                step=20.0,
                help="VLE interaction count in the last 30 days (must be >= 14 days clicks).",
            )

        avg_clicks_col, _ = st.columns([1.5, 2.5])
        with avg_clicks_col:
            average_clicks_per_active_day = st.number_input(
                "Average Clicks per Active Day",
                min_value=0.0,
                value=float(preset_data["average_clicks_per_active_day"]),
                step=0.5,
                help="Mean intensity of daily study sessions (total clicks / active days).",
            )

        st.markdown("<hr style='border-color: #F1F5F9; margin: 16px 0;'>", unsafe_allow_html=True)

        submit_predict = st.form_submit_button(
            "Run Advisory Risk Assessment",
            type="primary",
            use_container_width=True,
        )

    # Prediction Validation and Execution
    if submit_predict:
        validation_errors = []

        if not (clicks_last_7_days <= clicks_last_14_days <= clicks_last_30_days <= total_clicks):
            validation_errors.append(
                "Logical inconsistency in click counts: Clicks in 7 days must be <= 14 days <= 30 days <= Total clicks."
            )

        if active_days_last_30_days > active_days:
            validation_errors.append(
                "Active days in the last 30 days cannot exceed total active days."
            )

        if validation_errors:
            for err in validation_errors:
                st.error(f"**Input Validation Error:** {err}")
        else:
            payload = {
                "code_module": module,
                "code_presentation": presentation,
                "target_assessment_type": assessment_type,
                "target_date": float(target_date),
                "total_clicks": float(total_clicks),
                "activity_records": float(activity_records),
                "active_days": float(active_days),
                "active_days_last_30_days": float(active_days_last_30_days),
                "clicks_last_7_days": float(clicks_last_7_days),
                "clicks_last_14_days": float(clicks_last_14_days),
                "clicks_last_30_days": float(clicks_last_30_days),
                "average_clicks_per_active_day": float(average_clicks_per_active_day),
            }

            with st.spinner("Connecting to FastAPI backend and running Random Forest inference..."):
                response = predict_student_risk(payload, api_url=DEFAULT_API_URL)

            if response["success"]:
                pred_data = response["data"]
                st.session_state.latest_prediction = {
                    "payload": payload,
                    "result": pred_data,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                # Save to history
                st.session_state.prediction_history.insert(0, {
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "Module": module,
                    "Presentation": presentation,
                    "Assessment": assessment_type,
                    "Predicted Risk": f"{pred_data['predicted_probability']:.2%}",
                    "Status": "Review Recommended" if pred_data["flagged_for_review"] else "Below Threshold",
                    "Latency": f"{response['latency_ms']} ms",
                })
            else:
                st.error(f"**Prediction Request Failed:** {response['error']}")

    # Render Prediction Output if Available
    if st.session_state.latest_prediction:
        latest = st.session_state.latest_prediction
        p_res = latest["result"]
        p_load = latest["payload"]

        st.markdown("### 3. Prediction Result & Advisory Analysis")

        render_prediction_result_card(p_res, threshold=active_threshold)

        # Visual Probability Gauge
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        fig_gauge = render_probability_gauge(
            probability=p_res["predicted_probability"],
            threshold=active_threshold,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Expandable "Why was this student flagged?" Panel
        render_why_flagged_accordion(p_load)

    # Session History Table
    if st.session_state.prediction_history:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("### Session Assessment Log")
        hist_df = pd.DataFrame(st.session_state.prediction_history)
        st.dataframe(hist_df, use_container_width=True, hide_index=True)

        col_clear, _ = st.columns([1.5, 4.5])
        with col_clear:
            if st.button("Clear Session Log", key="clear_log_btn"):
                st.session_state.prediction_history = []
                st.session_state.latest_prediction = None
                st.rerun()


# ===========================================================================
# PAGE 3: BATCH ANALYTICS
# ===========================================================================
elif selected_page == "Batch Analytics":
    refresh = render_top_header(
        title="Batch Student Cohort Analytics",
        subtitle="Screen upcoming assessment cohorts in bulk using genuine backend prediction.",
        api_connected=api_connected,
        latency_ms=api_latency,
        model_name="Random Forest — Recall-Focused",
    )
    if refresh:
        st.rerun()

    render_html("""
    <div class="saas-card">
        <div class="card-title">Cohort Risk Screening Workflow</div>
        <p style="font-size: 13.5px; color: #4B5563; margin-bottom: 0; line-height: 1.5;">
            Upload a CSV containing student engagement records or load a pre-configured sample cohort extracted from 
            the verified 2014J held-out test data. Every valid record is transmitted directly to the real 
            <code>POST /predict</code> backend endpoint.
        </p>
    </div>
    """)

    batch_tab1, batch_tab2 = st.tabs(["1. Curated Sample Test Cohort (2014J)", "2. Upload Custom CSV"])

    records_to_process = None

    with batch_tab1:
        st.markdown("#### Curated Sample Test Cohort (20 Verified Test Records)")
        st.caption("Extracted directly from `data/processed/test.csv`. Represents real students from the 2014J held-out test set.")
        sample_df = pd.DataFrame(SAMPLE_BATCH_RECORDS)
        st.dataframe(sample_df.head(10), use_container_width=True, hide_index=True)

        col_btn, _ = st.columns([1.5, 3.5])
        with col_btn:
            if st.button("Run Batch Inference on Sample Cohort", type="primary", use_container_width=True):
                records_to_process = sample_df

    with batch_tab2:
        st.markdown("#### Upload Custom Cohort CSV")
        st.caption("CSV must contain the 12 required student engagement and assessment feature columns.")

        # Download Template CSV
        template_df = pd.DataFrame([SAMPLE_BATCH_RECORDS[0]])
        template_csv = template_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV Schema Template",
            data=template_csv,
            file_name="student_assessment_batch_template.csv",
            mime="text/csv",
        )

        uploaded_file = st.file_uploader(
            "Select CSV file for batch inference",
            type=["csv"],
            help="Upload a UTF-8 encoded CSV file with matching feature schema.",
        )

        if uploaded_file is not None:
            try:
                user_df = pd.read_csv(uploaded_file)
                st.success(f"Uploaded CSV contains {len(user_df):,} rows.")
                st.dataframe(user_df.head(5), use_container_width=True)

                if st.button("Run Batch Inference on Uploaded File", type="primary"):
                    records_to_process = user_df
            except Exception as e:
                st.error(f"Failed to read CSV: {str(e)}")

    # Execute Batch Processing if Triggered
    if records_to_process is not None:
        if not api_connected:
            st.error("Cannot perform batch inference: Prediction API is offline. Start the backend service first.")
        else:
            progress_bar = st.progress(0.0)
            status_text = st.empty()

            def update_progress(ratio, message):
                progress_bar.progress(ratio)
                status_text.caption(message)

            batch_res = predict_batch_records(
                records_to_process,
                api_url=DEFAULT_API_URL,
                progress_callback=update_progress,
                max_records=100,
            )

            progress_bar.empty()
            status_text.empty()

            if batch_res["success"]:
                st.session_state.batch_results = batch_res
                st.success(f"Batch prediction completed successfully for {batch_res['summary']['total_processed']} records.")
            else:
                st.error(f"Batch processing error: {batch_res['error']}")

    # Display Batch Results
    if st.session_state.batch_results:
        b_res = st.session_state.batch_results
        sum_data = b_res["summary"]
        res_df = b_res["results_df"]

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("### Batch Screening Summary")

        s1, s2, s3, s4, s5 = st.columns(5)
        with s1:
            render_kpi_card(
                title="Records Scanned",
                value=f"{sum_data['total_processed']:,}",
                explanation="Successfully scored via API.",
                border_accent=COLORS["primary_blue"],
            )
        with s2:
            render_kpi_card(
                title="Review Recommended",
                value=f"{sum_data['flagged_count']:,}",
                explanation=f"{sum_data['flagged_percentage']}% of cohort flagged.",
                border_accent=COLORS["risk_elevated"],
            )
        with s3:
            render_kpi_card(
                title="Below Threshold",
                value=f"{sum_data['safe_count']:,}",
                explanation="Within normal engagement bounds.",
                border_accent=COLORS["risk_low"],
            )
        with s4:
            render_kpi_card(
                title="Mean Risk Prob",
                value=f"{sum_data['mean_risk_probability']}%",
                explanation="Average cohort risk probability.",
                border_accent="#8B5CF6",
            )
        with s5:
            render_kpi_card(
                title="Throughput",
                value=f"{sum_data['records_per_second']}/s",
                explanation=f"Completed in {sum_data['total_inference_time_sec']}s.",
                border_accent=COLORS["light_blue"],
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown("### Interactive Cohort Results")

        # Filters
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            filter_status = st.selectbox("Filter by Review Status", ["All Records", "Flagged for Review Only", "Below Threshold Only"])
        with f_col2:
            available_modules = ["All Modules"] + sorted(res_df["Module"].unique().tolist())
            filter_module = st.selectbox("Filter by Module", available_modules)
        with f_col3:
            available_types = ["All Assessments"] + sorted(res_df["Assessment"].unique().tolist())
            filter_type = st.selectbox("Filter by Assessment Type", available_types)

        filtered_df = res_df.copy()
        if filter_status == "Flagged for Review Only":
            filtered_df = filtered_df[filtered_df["Flagged"] == True]
        elif filter_status == "Below Threshold Only":
            filtered_df = filtered_df[filtered_df["Flagged"] == False]

        if filter_module != "All Modules":
            filtered_df = filtered_df[filtered_df["Module"] == filter_module]

        if filter_type != "All Assessments":
            filtered_df = filtered_df[filtered_df["Assessment"] == filter_type]

        st.dataframe(
            filtered_df[[
                "Record #", "Module", "Presentation", "Assessment", "Days to Due",
                "Total Clicks", "Clicks (30d)", "Risk %", "Review Priority"
            ]],
            use_container_width=True,
            hide_index=True,
        )

        # Export Download Button
        csv_export = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Export Filtered Predictions to CSV",
            data=csv_export,
            file_name=f"student_risk_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

        st.caption(
            "Privacy Notice: All batch predictions are executed against the local FastAPI instance in-memory. "
            "No student data is stored persistently or transferred to external cloud networks."
        )


# ===========================================================================
# PAGE 4: MODEL PERFORMANCE (TECHNICAL DEEP DIVE)
# ===========================================================================
elif selected_page == "Model Performance":
    refresh = render_top_header(
        title="Model Performance & Evaluation",
        subtitle="Rigorous chronological held-out validation of the production Random Forest architecture.",
        api_connected=api_connected,
        latency_ms=api_latency,
        model_name="Random Forest — Recall-Focused",
    )
    if refresh:
        st.rerun()

    # Architecture Overview Card
    render_html(f"""
    <div class="saas-card">
        <div class="card-title">Production Model Architecture & Specifications</div>
        <div class="card-subtitle">Ensemble Random Forest Classifier with balanced subsample cost-sensitive weights</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-top: 10px;">
            <div>
                <span style="font-size: 11px; font-weight: 700; color: {COLORS['secondary_text']}; text-transform: uppercase;">Classifier Algorithm</span>
                <div style="font-size: 14px; font-weight: 700; color: {COLORS['deep_navy']};">RandomForestClassifier (scikit-learn)</div>
            </div>
            <div>
                <span style="font-size: 11px; font-weight: 700; color: {COLORS['secondary_text']}; text-transform: uppercase;">Hyperparameters</span>
                <div style="font-size: 14px; font-weight: 600; color: {COLORS['main_text']};">300 Trees, max_depth=15, min_samples_leaf=5</div>
            </div>
            <div>
                <span style="font-size: 11px; font-weight: 700; color: {COLORS['secondary_text']}; text-transform: uppercase;">Class Imbalance Handling</span>
                <div style="font-size: 14px; font-weight: 600; color: {COLORS['main_text']};"><code>class_weight='balanced_subsample'</code></div>
            </div>
            <div>
                <span style="font-size: 11px; font-weight: 700; color: {COLORS['secondary_text']}; text-transform: uppercase;">Decision Threshold</span>
                <div style="font-size: 14px; font-weight: 700; color: {COLORS['primary_blue']};">&tau; = {active_threshold:.5f} ({active_threshold:.2%})</div>
            </div>
        </div>
    </div>
    """)

    # Detailed Evaluation Metrics Table
    st.markdown("### Chronological Test Set Metrics (2014J Held-out Split)")
    metrics_table = pd.DataFrame({
        "Metric": [
            "Test Accuracy",
            "Balanced Accuracy",
            "Recall (Sensitivity)",
            "Precision (PPV)",
            "F1-Score",
            "ROC-AUC",
            "PR-AUC",
            "Total Evaluation Records",
            "Actual Positive Cases (<40)",
            "Model Flagged Students",
            "True Positives (TP)",
            "False Positives (FP)",
            "True Negatives (TN)",
            "False Negatives (FN)",
        ],
        "Score / Value": [
            "74.32%",
            "69.14%",
            "63.52%",
            "9.08%",
            "15.89%",
            "77.84%",
            "12.90%",
            "41,062 records",
            "1,568 cases (3.82%)",
            "10,967 students (26.71%)",
            "996 students",
            "9,971 students",
            "29,523 students",
            "572 students",
        ],
        "Operational Significance": [
            "Overall accuracy across normal and struggling student populations.",
            "Average of sensitivity and specificity; robust to extreme class imbalance.",
            "Proportion of true failing scores successfully intercepted for advisor review.",
            "Proportion of flagged records that were truly low scores (<40).",
            "Harmonic mean balancing precision and recall at threshold 0.2457.",
            "Strong discrimination ability across all potential operational thresholds.",
            "High benchmark on highly skewed positive class (3.82% base prevalence).",
            "Strictly held-out future academic term (2014J); no data leakage.",
            "Severe real-world class imbalance typical of university coursework.",
            "Total alert volume routed to academic advising triage systems.",
            "Students correctly intercepted before failing their assessment.",
            "Students flagged who scored >=40; drives advising review workload.",
            "Correctly identified normal engagement; no alert generated.",
            "Students scoring <40 whom the model failed to intercept.",
        ],
    })
    st.dataframe(metrics_table, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Charts Grid
    mp_col1, mp_col2 = st.columns([1.1, 1.1])
    with mp_col1:
        st.plotly_chart(render_confusion_matrix_chart(), use_container_width=True)

    with mp_col2:
        st.plotly_chart(render_feature_importance_chart(), use_container_width=True)

    # In-Depth Pedagogical Trade-off Section
    render_html(f"""
    <div class="saas-card">
        <div class="card-title">Comprehensive Trade-off Analysis: Why Recall Was Prioritized</div>
        <div class="card-subtitle">Bridging machine learning evaluation with academic advisory operations</div>
        <div style="font-size: 13.5px; color: {COLORS['main_text']}; line-height: 1.6;">
            <p>
                A standard Machine Learning classifier tuned for default accuracy or maximum F1 (e.g. threshold 0.458) 
                would flag significantly fewer students. However, in our validation experiments, that conservative approach 
                resulted in a recall of only <strong>35.3%</strong>, failing to detect nearly two out of every three struggling students.
            </p>
            <p>
                By selecting <code>&tau; = 0.24567</code> on the 2014B validation cohort, the model achieves 
                <strong>63.52% recall</strong> on the held-out 2014J test set. In concrete terms:
            </p>
            <ul>
                <li><strong>996 struggling students</strong> are proactively identified for timely academic support.</li>
                <li>Only <strong>572 low-score cases</strong> are missed, compared to over 1,000 missed under default settings.</li>
                <li>The cost of this sensitivity is <strong>9,971 false positives</strong> across 41,062 assessment records.</li>
            </ul>
            <p>
                <strong>Mitigating Educator Fatigue:</strong> Advising teams should never use flags to issue punitive warnings. 
                Instead, alerts can trigger supportive digital nudges (e.g., <em>"Reminder: TMA-02 submission deadline is in 10 days. 
                Writing center workshops are open this Wednesday"</em>). This creates positive educational outcomes even for false-positive recipients.
            </p>
        </div>
    </div>
    """)


# ===========================================================================
# PAGE 5: ABOUT & METHODOLOGY
# ===========================================================================
elif selected_page == "About & Methodology":
    refresh = render_top_header(
        title="About & Methodology",
        subtitle="Data provenance, experimental splitting rigor, and the ethical charter governing model deployment.",
        api_connected=api_connected,
        latency_ms=api_latency,
        model_name="Random Forest — Recall-Focused",
    )
    if refresh:
        st.rerun()

    render_html("""
    <div class="saas-card">
        <div class="card-title">Dataset Provenance & Formulation</div>
        <div class="card-subtitle">Open University Learning Analytics Dataset (OULAD)</div>
        <p style="font-size: 13.5px; color: #1F2937; line-height: 1.6;">
            The <strong>Open University Learning Analytics Dataset (OULAD)</strong> is one of the most comprehensive public learning analytics datasets, 
            containing data from 32,593 students across 22 presentation cohorts and 7 distinct undergraduate modules.
        </p>
        <p style="font-size: 13.5px; color: #1F2937; line-height: 1.6; margin-bottom: 0;">
            <strong>Target Formulation:</strong> In this system, the model predicts whether a student will score strictly below 40 points (&lt;40) 
            on their next eligible Tutor-Marked Assessment (TMA) or Computer-Marked Assessment (CMA). A score of 40 represents the official 
            passing threshold across the Open University curriculum.
        </p>
    </div>
    """)

    col_meth1, col_meth2 = st.columns(2)

    with col_meth1:
        render_html(f"""
        <div class="saas-card" style="height: 100%;">
            <div class="card-title">Strict Chronological Splitting</div>
            <div class="card-subtitle">Zero data leakage across academic terms</div>
            <p style="font-size: 13px; color: {COLORS['main_text']}; line-height: 1.55;">
                Standard random k-fold cross-validation is fundamentally flawed for educational time-series because it leaks future curriculum 
                adjustments into the training set. This system employs strict <strong>chronological presentation splitting</strong>:
            </p>
            <ul style="font-size: 12.5px; color: {COLORS['secondary_text']}; line-height: 1.5; padding-left: 18px;">
                <li><strong>Training Data:</strong> 2013B and 2013J presentations (historical past).</li>
                <li><strong>Validation Data:</strong> 2014B presentation (intermediate cohort used solely for model selection and threshold tuning).</li>
                <li><strong>Test Data:</strong> 2014J presentation (held-out future academic cohort; evaluated once without tuning).</li>
            </ul>
        </div>
        """)

    with col_meth2:
        render_html(f"""
        <div class="saas-card" style="height: 100%;">
            <div class="card-title">Threshold Tuning Rationale</div>
            <div class="card-subtitle">Validation-derived decision boundary (&tau; = 0.24567)</div>
            <p style="font-size: 13px; color: {COLORS['main_text']}; line-height: 1.55;">
                In the 2014B validation set, candidate thresholds were systematically evaluated against recall targets. 
                A decision threshold of <code>&tau; = 0.24567134268537077</code> was identified as the optimal operating point to achieve 
                &ge;60% recall on the low-score class.
            </p>
            <p style="font-size: 13px; color: {COLORS['main_text']}; line-height: 1.55;">
                Crucially, this threshold was frozen prior to test evaluation. It was applied unchanged to the 2014J held-out test data, 
                where it successfully yielded 63.52% recall, verifying strong generalizability across cohorts.
            </p>
        </div>
        """)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Critical Limitations Box
    render_html(f"""
    <div class="saas-card" style="border-left: 4px solid {COLORS['risk_moderate']};">
        <div class="card-title">Critical System Limitations</div>
        <div class="card-subtitle">Transparent disclosure of machine learning boundaries in education</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; font-size: 13px; color: {COLORS['main_text']};">
            <div>
                <strong>1. Clicks Are Proxies, Not Learning:</strong> VLE click volumes reflect digital resource access, not cognitive comprehension, 
                offline textbook study, or active classroom participation.
            </div>
            <div>
                <strong>2. Institutional Transferability:</strong> Models trained on UK Open University distance learners may not generalize to 
                in-person colleges with different assessment cadences.
            </div>
            <div>
                <strong>3. Probabilistic Signals, Not Facts:</strong> Model outputs represent empirical probability estimates based on historical patterns, 
                never deterministic guarantees of individual student capability.
            </div>
            <div>
                <strong>4. Correlation vs. Causation:</strong> Permutation importance demonstrates feature predictive value across populations; 
                it does not prove that modifying a specific behavior will automatically alter a grade.
            </div>
        </div>
    </div>
    """)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Formal Ethical-Use Charter
    render_html(f"""
    <div class="saas-card" style="border: 1.5px solid {COLORS['primary_blue']}; background: #FAFCFF;">
        <div class="card-title" style="color: {COLORS['dark_blue']};">Formal Ethical-Use Charter</div>
        <div class="card-subtitle">Binding governance standards for institutions deploying Student Insight AI</div>
        <blockquote style="border-left: 3px solid {COLORS['primary_blue']}; margin: 12px 0; padding-left: 14px; font-size: 14px; color: {COLORS['deep_navy']}; font-style: italic; line-height: 1.5;">
            "This tool is designed to support educators in identifying students who may benefit from additional academic attention. 
            It must not be used as an automated grading, disciplinary, admission, or exclusion system."
        </blockquote>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; margin-top: 14px; font-size: 12.5px; color: {COLORS['secondary_text']};">
            <div>
                <strong>Prohibited Use 1:</strong> Automated punitive grading or grade deductions based on engagement metrics.
            </div>
            <div>
                <strong>Prohibited Use 2:</strong> Revocation of scholarships, bursaries, or academic standing based on model alerts.
            </div>
            <div>
                <strong>Prohibited Use 3:</strong> Mandatory course withdrawals without exhaustive human advisor consultation.
            </div>
            <div>
                <strong>Mandatory Requirement:</strong> Every flagged record must be reviewed by an authorized academic professional.
            </div>
        </div>
    </div>
    """)


# ===========================================================================
# PAGE 6: API STATUS & DIAGNOSTICS
# ===========================================================================
elif selected_page == "API Status":
    refresh = render_top_header(
        title="API Health & Diagnostics",
        subtitle="Real-time monitoring of backend microservices, inference latency, and endpoint contracts.",
        api_connected=api_connected,
        latency_ms=api_latency,
        model_name="Random Forest — Recall-Focused",
    )
    if refresh:
        st.rerun()

    # System Diagnostics Card
    st.markdown("### Backend Service Health")

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        render_kpi_card(
            title="Service Status",
            value="ONLINE" if api_connected else "OFFLINE",
            explanation="FastAPI HTTP ping response.",
            border_accent=COLORS["risk_low"] if api_connected else COLORS["risk_elevated"],
        )
    with d2:
        render_kpi_card(
            title="Inference Model",
            value="LOADED" if api_health["model_loaded"] else "UNAVAILABLE",
            explanation=api_health["model"],
            border_accent=COLORS["primary_blue"],
        )
    with d3:
        render_kpi_card(
            title="Round-trip Latency",
            value=f"{api_latency:.1f} ms" if api_connected else "—",
            explanation="Network health ping duration.",
            border_accent=COLORS["light_blue"],
        )
    with d4:
        render_kpi_card(
            title="Operating Threshold",
            value=f"{active_threshold:.4f}",
            explanation="Validation-tuned decision boundary.",
            border_accent="#8B5CF6",
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    if not api_connected:
        render_html(f"""
        <div class="saas-card" style="border-left: 4px solid {COLORS['risk_elevated']};">
            <div class="card-title" style="color: {COLORS['risk_elevated']};">Backend Connection Error</div>
            <p style="font-size: 13.5px; color: {COLORS['main_text']}; line-height: 1.5;">
                The Streamlit dashboard is unable to reach the FastAPI prediction backend at <code>{DEFAULT_API_URL}</code>.
            </p>
            <div style="background: #0F172A; border-radius: 8px; padding: 14px; margin: 12px 0;">
                <span style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Launch Command (PowerShell):</span>
                <pre style="color: #38BDF8; font-family: monospace; font-size: 13px; margin: 6px 0 0 0;">python -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000</pre>
            </div>
            <div style="font-size: 12.5px; color: {COLORS['secondary_text']};">
                <strong>Troubleshooting Steps:</strong>
                <ol style="padding-left: 18px; margin: 6px 0 0 0; line-height: 1.5;">
                    <li>Ensure you are running commands from the project root: <code>E:\Student-At-Risk-Prediction</code>.</li>
                    <li>Verify the virtual environment is activated: <code>.\.venv\Scripts\Activate.ps1</code>.</li>
                    <li>Verify port 8000 is not occupied by another process.</li>
                </ol>
            </div>
        </div>
        """)
    else:
        st.success("FastAPI microservice is operational and responding to health probes.")

    # Endpoint Catalog & Contracts
    st.markdown("### API Endpoint Catalog & Schema Inspector")

    ep_tab1, ep_tab2, ep_tab3 = st.tabs(["POST /predict", "GET /health", "GET /"])

    with ep_tab1:
        st.markdown("#### `POST /predict` — Run Student Inference")
        st.caption("Receives single student engagement features and returns probabilistic risk assessment.")
        col_sch1, col_sch2 = st.columns(2)
        with col_sch1:
            st.markdown("**Request Payload Schema (JSON):**")
            st.code("""{
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
  "average_clicks_per_active_day": 23.23
}""", language="json")
        with col_sch2:
            st.markdown("**Response Schema (JSON):**")
            st.code("""{
  "predicted_probability": 0.0890,
  "threshold": 0.24567134268537077,
  "flagged_for_review": false,
  "risk_band": "Below review threshold",
  "decision_policy": "Recall-focused threshold selected on validation data",
  "status": "Not flagged by this model",
  "message": "This is an advisory prediction, not a confirmed outcome. A qualified educator must review the student's circumstances."
}""", language="json")

    with ep_tab2:
        st.markdown("#### `GET /health` — Service Health Check")
        st.code("""{
  "status": "healthy",
  "model_loaded": true,
  "model": "Random Forest - Recall Focused",
  "threshold": 0.24567134268537077
}""", language="json")

    with ep_tab3:
        st.markdown("#### `GET /` — API Metadata")
        st.code("""{
  "message": "Student At-Risk Prediction API is running",
  "model": "Random Forest - Recall Focused",
  "threshold": 0.24567134268537077,
  "model_file": "random_forest.joblib",
  "decision_policy": "Recall-focused; human review required"
}""", language="json")


# ---------------------------------------------------------------------------
# GLOBAL FOOTER
# ---------------------------------------------------------------------------
st.markdown("<hr style='border-color: #E2E8F0; margin: 30px 0 15px 0;'>", unsafe_allow_html=True)
render_html(f"""
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; font-size: 12px; color: {COLORS['secondary_text']};">
    <div>
        <strong>Student Insight AI</strong> &bull; Advisory Decision Support Platform &bull; Model: Random Forest v1.0
    </div>
    <div>
        Data: OULAD &bull; Threshold: {active_threshold:.4f} &bull; For authorized academic advisory use only.
    </div>
</div>
""")
