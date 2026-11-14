"""
UI Components and Visualizations for the Student Insight AI Platform.
Features custom CSS design tokens, Plotly charts, and reusable SaaS widgets.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional, List

from src.dashboard.config import (
    COLORS,
    MODEL_METADATA,
    VERIFIED_METRICS,
    CONFUSION_MATRIX,
    FEATURE_IMPORTANCE_DATA,
)


def render_html(raw_html: str):
    """
    Renders pure HTML cleanly without allowing markdown indentation
    to convert HTML into pre/code blocks. Strips leading whitespace per line
    and uses st.html() or unindented st.markdown(..., unsafe_allow_html=True).
    """
    clean_lines = [line.strip() for line in raw_html.strip().splitlines() if line.strip()]
    clean_html = "\n".join(clean_lines)
    if hasattr(st, "html"):
        st.html(clean_html)
    else:
        st.markdown(clean_html, unsafe_allow_html=True)


def inject_custom_css():
    """
    Injects custom CSS adhering strictly to the design system:
    Primary blue, deep navy, dark blue, clean light SaaS canvas (#F7F9FC),
    white cards (#FFFFFF), crisp borders (#E5E7EB), and careful risk colors.
    """
    css_content = f"""
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global Typography & Canvas */
    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: {COLORS["background"]};
        color: {COLORS["main_text"]};
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {COLORS["deep_navy"]};
        border-right: 1px solid #1E293B;
    }}
    [data-testid="stSidebar"] * {{
        color: #F8FAFC !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: #1E293B !important;
    }}
    [data-testid="stSidebar"] .stRadio > label {{
        color: #94A3B8 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        margin-bottom: 8px !important;
    }}
    [data-testid="stSidebar"] div[role="radiogroup"] label {{
        background: transparent;
        padding: 8px 12px;
        border-radius: 8px;
        transition: all 0.15s ease-in-out;
        margin-bottom: 2px;
    }}
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
        background: rgba(255, 255, 255, 0.06);
    }}

    /* Top App Header / Navbar Container */
    .top-header-container {{
        background: {COLORS["card_bg"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
        padding: 18px 24px;
        margin-bottom: 22px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }}
    .header-title-text {{
        font-size: 24px;
        font-weight: 800;
        color: {COLORS["deep_navy"]};
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.2;
    }}
    .header-sub-text {{
        font-size: 13.5px;
        color: {COLORS["secondary_text"]};
        margin-top: 4px;
        margin-bottom: 0;
    }}

    /* KPI Cards */
    .kpi-card {{
        background: {COLORS["card_bg"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .kpi-card:hover {{
        border-color: #CBD5E1;
        box-shadow: 0 4px 6px -1px rgba(16, 24, 40, 0.08);
    }}
    .kpi-title {{
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {COLORS["secondary_text"]};
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .kpi-value {{
        font-size: 26px;
        font-weight: 800;
        color: {COLORS["deep_navy"]};
        margin: 8px 0 4px 0;
        letter-spacing: -0.02em;
    }}
    .kpi-caption {{
        font-size: 12.5px;
        color: {COLORS["secondary_text"]};
        line-height: 1.35;
        margin: 0;
    }}

    /* Policy Callout Card */
    .policy-box {{
        background: #F8FAFC;
        border-left: 4px solid {COLORS["primary_blue"]};
        border-top: 1px solid {COLORS["border"]};
        border-right: 1px solid {COLORS["border"]};
        border-bottom: 1px solid {COLORS["border"]};
        border-radius: 0 12px 12px 0;
        padding: 18px 22px;
        margin: 20px 0;
    }}
    .policy-title {{
        font-size: 15px;
        font-weight: 700;
        color: {COLORS["dark_blue"]};
        margin-bottom: 6px;
    }}
    .policy-text {{
        font-size: 13.5px;
        color: {COLORS["main_text"]};
        line-height: 1.5;
        margin: 0;
    }}

    /* Section Cards / Surfaces */
    .saas-card {{
        background: {COLORS["card_bg"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
    }}
    .card-title {{
        font-size: 16px;
        font-weight: 700;
        color: {COLORS["deep_navy"]};
        margin-bottom: 4px;
    }}
    .card-subtitle {{
        font-size: 13px;
        color: {COLORS["secondary_text"]};
        margin-bottom: 16px;
    }}

    /* Status Badges */
    .badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.01em;
    }}
    .badge-online {{
        background: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
    }}
    .badge-offline {{
        background: #FEE2E2;
        color: #B91C1C;
        border: 1px solid #FCA5A5;
    }}
    .badge-model {{
        background: #EFF6FF;
        color: {COLORS["primary_blue"]};
        border: 1px solid #BFDBFE;
    }}
    .badge-flagged {{
        background: {COLORS["risk_elevated_bg"]};
        color: {COLORS["risk_elevated"]};
        border: 1px solid {COLORS["risk_elevated_border"]};
    }}
    .badge-safe {{
        background: {COLORS["risk_low_bg"]};
        color: {COLORS["risk_low"]};
        border: 1px solid {COLORS["risk_low_border"]};
    }}

    /* Buttons */
    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {{
        background-color: {COLORS["primary_blue"]};
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        padding: 10px 20px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
        transition: background-color 0.15s ease;
    }}
    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button[kind="primary"]:hover {{
        background-color: #1D4ED8;
    }}
    div.stButton > button[kind="secondary"] {{
        background-color: white;
        color: {COLORS["main_text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        font-weight: 500;
    }}
    div.stButton > button[kind="secondary"]:hover {{
        background-color: #F8FAFC;
        border-color: #CBD5E1;
    }}

    /* Custom Form Input Styling */
    div[data-testid="stForm"] {{
        background: {COLORS["card_bg"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
    }}
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {{
        border-radius: 8px !important;
        border: 1px solid {COLORS["border"]} !important;
        font-size: 14px !important;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: {COLORS["primary_blue"]} !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15) !important;
    }}

    /* Pulsing Status Dot */
    .status-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }}
    .dot-green {{
        background-color: #16A34A;
        box-shadow: 0 0 0 2px rgba(22, 163, 74, 0.2);
    }}
    .dot-red {{
        background-color: #DC2626;
        box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.2);
    }}

    /* Clean Streamlit metric overrides */
    div[data-testid="stMetric"] {{
        background-color: {COLORS["card_bg"]};
        border: 1px solid {COLORS["border"]};
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }}
    div[data-testid="stMetricLabel"] {{
        color: {COLORS["secondary_text"]} !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: {COLORS["deep_navy"]} !important;
        font-weight: 800 !important;
    }}

    /* Table & Dataframe tweaks */
    div[data-testid="stDataFrame"] {{
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        overflow: hidden;
    }}

    /* Hide Streamlit default hamburger menu & footer cleanly */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{background: transparent;}}

    /* Responsive adjustments */
    @media (max-width: 768px) {{
        .top-header-container {{
            flex-direction: column;
            align-items: flex-start;
        }}
        .kpi-value {{
            font-size: 22px;
        }}
    }}
    """
    clean_css = "\n".join(line.strip() for line in css_content.strip().splitlines() if line.strip())
    st.markdown(f"<style>{clean_css}</style>", unsafe_allow_html=True)


def render_top_header(
    title: str,
    subtitle: str,
    api_connected: bool,
    latency_ms: float = 0.0,
    model_name: str = MODEL_METADATA["variant"],
    show_refresh: bool = True,
) -> bool:
    """
    Renders the consistent top SaaS header with title, subtitle, live backend badge,
    active model badge, and real refresh button. Returns True if refresh was clicked.
    """
    status_class = "badge-online" if api_connected else "badge-offline"
    status_dot = "dot-green" if api_connected else "dot-red"
    status_label = f"API Online ({latency_ms:.0f}ms)" if api_connected else "API Offline"

    header_cols = st.columns([3.5, 1.5])
    with header_cols[0]:
        render_html(f"""
        <div style="margin-bottom: 12px;">
            <h1 class="header-title-text">{title}</h1>
            <p class="header-sub-text">{subtitle}</p>
        </div>
        """)

    refresh_clicked = False
    with header_cols[1]:
        render_html(f"""
        <div style="display: flex; gap: 8px; justify-content: flex-end; align-items: center; margin-bottom: 6px; flex-wrap: wrap;">
            <span class="badge {status_class}">
                <span class="status-dot {status_dot}"></span> {status_label}
            </span>
            <span class="badge badge-model">
                {model_name}
            </span>
        </div>
        """)
        if show_refresh:
            subcols = st.columns([1, 1])
            with subcols[1]:
                if st.button("Refresh", key="hdr_refresh_btn", use_container_width=True):
                    refresh_clicked = True

    return refresh_clicked


def render_sidebar_nav(api_connected: bool, active_threshold: float) -> str:
    """
    Renders the brand sidebar with logo, navigation links, and system tray metadata.
    Returns the selected page name.
    """
    with st.sidebar:
        # App Logo & Brand Header
        render_html(f"""
        <div style="padding: 12px 0 16px 0; border-bottom: 1px solid #1E293B;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 36px; height: 36px; border-radius: 8px; background: linear-gradient(135deg, {COLORS['primary_blue']}, #1D4ED8); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px; color: white;">
                    AI
                </div>
                <div>
                    <div style="font-size: 16px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em; line-height: 1.1;">Student Insight AI</div>
                    <div style="font-size: 11px; color: #94A3B8; font-weight: 500;">Academic Analytics Platform</div>
                </div>
            </div>
        </div>
        """)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Main Navigation
        page = st.radio(
            "PLATFORM NAVIGATION",
            [
                "Dashboard",
                "Student Risk Assessment",
                "Batch Analytics",
                "Model Performance",
                "About & Methodology",
                "API Status",
            ],
            index=0,
            label_visibility="visible",
        )

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # System Tray / Persistent Metadata
        status_bg = "#064E3B" if api_connected else "#7F1D1D"
        status_text_color = "#34D399" if api_connected else "#F87171"
        status_txt = "Backend Online" if api_connected else "Backend Offline"

        render_html(f"""
        <div style="background: #0F172A; border: 1px solid #1E293B; border-radius: 10px; padding: 14px; margin-top: auto;">
            <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                System Metadata
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 12px;">
                <span style="color: #94A3B8;">Model:</span>
                <span style="color: #F8FAFC; font-weight: 600;">Random Forest v1.0</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 12px;">
                <span style="color: #94A3B8;">Threshold (τ):</span>
                <span style="color: #60A5FA; font-weight: 600;">{active_threshold:.4f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 12px;">
                <span style="color: #94A3B8;">Dataset:</span>
                <span style="color: #F8FAFC; font-weight: 600;">OULAD (2014J)</span>
            </div>
            <div style="background: {status_bg}; color: {status_text_color}; border-radius: 6px; padding: 6px 10px; font-size: 11px; font-weight: 600; text-align: center;">
                ● {status_txt}
            </div>
        </div>
        <div style="margin-top: 14px; text-align: center; font-size: 11px; color: #64748B;">
            Educational Advisory Support System
        </div>
        """)

    return page


def render_kpi_card(
    title: str,
    value: str,
    explanation: str,
    tooltip: Optional[str] = None,
    border_accent: Optional[str] = None,
):
    """
    Renders an executive KPI card with title, formatted value, and explanation.
    """
    accent_style = f"border-top: 3px solid {border_accent};" if border_accent else ""
    tooltip_html = f'<span title="{tooltip}" style="cursor: help; color: #9CA3AF; font-size: 12px;">ℹ</span>' if tooltip else ""

    render_html(f"""
    <div class="kpi-card" style="{accent_style}">
        <div>
            <div class="kpi-title">
                <span>{title}</span>
                {tooltip_html}
            </div>
            <div class="kpi-value">{value}</div>
        </div>
        <div class="kpi-caption">{explanation}</div>
    </div>
    """)


def render_policy_banner(threshold: float = MODEL_METADATA["threshold"]):
    """
    Renders the required prominent model policy callout.
    """
    render_html(f"""
    <div class="policy-box">
        <div class="policy-title">
            Random Forest — Recall-Focused Model &bull; Decision Threshold: {threshold:.5f} ({threshold:.2%})
        </div>
        <p class="policy-text">
            <strong>Operating Policy:</strong> The model prioritizes identifying students who may benefit from academic support. 
            This increases the number of students flagged for review and also produces false positives. 
            <strong>Predictions must be reviewed by an educator.</strong> This tool provides advisory signals and must never 
            be used for automated grading, exclusion, or disciplinary measures.
        </p>
    </div>
    """)


def render_confusion_matrix_chart(
    tn: int = CONFUSION_MATRIX["true_negatives"],
    fp: int = CONFUSION_MATRIX["false_positives"],
    fn: int = CONFUSION_MATRIX["false_negatives"],
    tp: int = CONFUSION_MATRIX["true_positives"],
) -> go.Figure:
    """
    Renders an interactive, clearly labeled Confusion Matrix heatmap using Plotly.
    Orientation is explicitly stated: Actual Class (Rows) vs Model Screening (Columns).
    """
    total = tn + fp + fn + tp
    actual_normal = tn + fp
    actual_low = fn + tp

    z_values = [[tn, fp], [fn, tp]]
    
    text_annotations = [
        [
            f"<b>True Negative (TN)</b><br>{tn:,}<br>({(tn/actual_normal):.1%} of normal)",
            f"<b>False Positive (FP)</b><br>{fp:,}<br>({(fp/actual_normal):.1%} of normal)",
        ],
        [
            f"<b>False Negative (FN)</b><br>{fn:,}<br>({(fn/actual_low):.1%} of low scores)",
            f"<b>True Positive (TP)</b><br>{tp:,}<br>({(tp/actual_low):.1%} of low scores)",
        ],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=["Predicted: Not Flagged (Normal)", "Predicted: Flagged for Review"],
            y=["Actual: Score &ge; 40 (Normal)", "Actual: Score &lt; 40 (At-Risk)"],
            text=text_annotations,
            texttemplate="%{text}",
            textfont={"size": 13, "family": "Inter, sans-serif"},
            colorscale=[
                [0.0, "#EFF6FF"],
                [0.2, "#DBEAFE"],
                [0.6, "#93C5FD"],
                [1.0, "#2563EB"],
            ],
            showscale=False,
            hoverongaps=False,
        )
    )

    fig.update_layout(
        title={
            "text": f"<b>Confusion Matrix — Held-Out Test Set 2014J (N = {total:,})</b>",
            "font": {"size": 14, "color": COLORS["deep_navy"], "family": "Inter"},
            "x": 0.02,
        },
        xaxis={
            "title": "<b>Model Screening Classification (Threshold = 24.57%)</b>",
            "side": "bottom",
            "tickfont": {"size": 12, "color": COLORS["main_text"]},
        },
        yaxis={
            "title": "<b>Actual Academic Outcome</b>",
            "autorange": "reversed",
            "tickfont": {"size": 12, "color": COLORS["main_text"]},
        },
        margin=dict(l=40, r=20, t=50, b=40),
        height=340,
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig


def render_feature_importance_chart(features: List[Dict[str, Any]] = FEATURE_IMPORTANCE_DATA) -> go.Figure:
    """
    Renders an interactive horizontal bar chart for verified permutation feature importances.
    """
    df = pd.DataFrame(features).sort_values("importance_mean", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=df["importance_mean"],
            y=df["display_name"],
            orientation="h",
            error_x=dict(
                type="data",
                array=df["importance_std"],
                visible=True,
                color="#64748B",
                thickness=1.5,
            ),
            marker=dict(
                color=COLORS["primary_blue"],
                line=dict(color="#1D4ED8", width=1),
            ),
            hovertemplate="<b>%{y}</b><br>Permutation Importance: %{x:.4f} ± %{error_x.array:.4f}<extra></extra>",
        )
    )

    fig.update_layout(
        title={
            "text": "<b>Validation Permutation Feature Importance (Validation 2014B)</b>",
            "font": {"size": 14, "color": COLORS["deep_navy"], "family": "Inter"},
            "x": 0.02,
        },
        xaxis={
            "title": "<b>Drop in Evaluation Score when Feature is Permuted</b>",
            "tickformat": ".3f",
            "gridcolor": "#F1F5F9",
        },
        yaxis={
            "title": "",
            "tickfont": {"size": 11.5, "color": COLORS["main_text"]},
        },
        margin=dict(l=20, r=30, t=45, b=40),
        height=420,
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig


def render_benchmark_chart(models: List[Dict[str, Any]]) -> go.Figure:
    """
    Renders a multi-metric comparative bar chart across candidate models.
    """
    df = pd.DataFrame(models)

    metrics = [
        ("Recall", "recall", "#2563EB"),
        ("ROC-AUC", "roc_auc", "#60A5FA"),
        ("Balanced Acc", "balanced_acc", "#94A3B8"),
        ("Precision", "precision", "#F59E0B"),
    ]

    fig = go.Figure()

    for label, col, color in metrics:
        fig.add_trace(
            go.Bar(
                name=label,
                x=df["model"],
                y=df[col],
                marker_color=color,
                hovertemplate=f"<b>%{{x}}</b><br>{label}: %{{y:.2%}}<extra></extra>",
            )
        )

    fig.update_layout(
        barmode="group",
        title={
            "text": "<b>Cross-Model Evaluation Comparison (Validation Split)</b>",
            "font": {"size": 14, "color": COLORS["deep_navy"], "family": "Inter"},
            "x": 0.02,
        },
        yaxis={
            "title": "<b>Metric Score (0 - 1.0)</b>",
            "tickformat": ".0%",
            "range": [0, 1.0],
            "gridcolor": "#F1F5F9",
        },
        xaxis={"title": ""},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font={"size": 11},
        ),
        margin=dict(l=40, r=20, t=50, b=40),
        height=340,
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig


def render_probability_gauge(probability: float, threshold: float = MODEL_METADATA["threshold"]) -> go.Figure:
    """
    Visualizes the prediction probability relative to the selected review threshold.
    Shows the probability and threshold clearly and separately.
    """
    flagged = probability >= threshold
    bar_color = COLORS["risk_elevated"] if flagged else COLORS["risk_low"]

    fig = go.Figure()

    # Base background track (0 to 1)
    fig.add_trace(
        go.Bar(
            x=[1.0],
            y=["Assessment Risk"],
            orientation="h",
            marker=dict(color="#F1F5F9", line=dict(color="#E2E8F0", width=1)),
            hoverinfo="none",
            showlegend=False,
        )
    )

    # Active probability fill
    fig.add_trace(
        go.Bar(
            x=[min(max(probability, 0.0), 1.0)],
            y=["Assessment Risk"],
            orientation="h",
            marker=dict(color=bar_color),
            hovertemplate=f"Predicted Risk Probability: {probability:.2%}<extra></extra>",
            showlegend=False,
        )
    )

    # Threshold indicator vertical line
    fig.add_vline(
        x=threshold,
        line_width=2.5,
        line_dash="dash",
        line_color=COLORS["deep_navy"],
        annotation_text=f"Review Threshold: {threshold:.2%}",
        annotation_position="top",
        annotation_font=dict(size=12, color=COLORS["deep_navy"], family="Inter"),
    )

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(
            range=[0, 1.0],
            tickformat=".0%",
            title="<b>Predicted Probability of Score &lt; 40</b>",
            gridcolor="#F8FAFC",
        ),
        yaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=35, b=30),
        height=130,
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig


def render_prediction_result_card(
    result: Dict[str, Any],
    threshold: float = MODEL_METADATA["threshold"],
):
    """
    Presents the prediction results cleanly, showing probability, threshold,
    review status, and human review recommendation.
    """
    prob = float(result.get("predicted_probability", 0.0))
    flagged = bool(result.get("flagged_for_review", False))

    if flagged:
        badge_html = f'<span class="badge badge-flagged" style="font-size: 13px; padding: 5px 12px;">Review Recommended</span>'
        banner_border = COLORS["risk_elevated"]
        advisory_title = "Educator Review Recommended"
        advisory_text = (
            "The model has identified student engagement patterns consistent with peers who scored below 40 on upcoming coursework. "
            "<strong>This is an advisory signal, not a diagnosis of ability or fault.</strong> "
            "Please review the student's submission history and consider reaching out to offer academic guidance."
        )
        box_bg = COLORS["risk_elevated_bg"]
    else:
        badge_html = f'<span class="badge badge-safe" style="font-size: 13px; padding: 5px 12px;">Below Review Threshold</span>'
        banner_border = COLORS["risk_low"]
        advisory_title = "Below Current Review Threshold"
        advisory_text = (
            "The model did not flag this student at the selected 24.57% recall-focused threshold. "
            "<strong>This does not guarantee a successful assessment score.</strong> "
            "Routine academic monitoring should continue as standard practice."
        )
        box_bg = COLORS["risk_low_bg"]

    render_html(f"""
    <div style="background: white; border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 22px; margin-top: 18px; box-shadow: 0 2px 4px rgba(16,24,40,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid {COLORS['border']}; padding-bottom: 14px; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
            <div>
                <span style="font-size: 12px; font-weight: 700; color: {COLORS['secondary_text']}; text-transform: uppercase; letter-spacing: 0.05em;">Prediction Inference Result</span>
                <h3 style="margin: 2px 0 0 0; color: {COLORS['deep_navy']}; font-weight: 800;">{result.get('risk_band', 'Assessment Risk Report')}</h3>
            </div>
            <div>{badge_html}</div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 18px;">
            <div style="background: #F8FAFC; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 12px 14px;">
                <div style="font-size: 11px; font-weight: 600; color: {COLORS['secondary_text']}; text-transform: uppercase;">Predicted Risk Probability</div>
                <div style="font-size: 24px; font-weight: 800; color: {COLORS['deep_navy']}; margin-top: 2px;">{prob:.2%}</div>
            </div>
            <div style="background: #F8FAFC; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 12px 14px;">
                <div style="font-size: 11px; font-weight: 600; color: {COLORS['secondary_text']}; text-transform: uppercase;">Review Threshold (&tau;)</div>
                <div style="font-size: 24px; font-weight: 800; color: {COLORS['primary_blue']}; margin-top: 2px;">{threshold:.2%}</div>
            </div>
            <div style="background: #F8FAFC; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 12px 14px;">
                <div style="font-size: 11px; font-weight: 600; color: {COLORS['secondary_text']}; text-transform: uppercase;">Decision Status</div>
                <div style="font-size: 16px; font-weight: 700; color: {COLORS['main_text']}; margin-top: 6px;">{'Flagged for Review' if flagged else 'Unflagged'}</div>
            </div>
            <div style="background: #F8FAFC; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 12px 14px;">
                <div style="font-size: 11px; font-weight: 600; color: {COLORS['secondary_text']}; text-transform: uppercase;">Inference Engine</div>
                <div style="font-size: 13.5px; font-weight: 600; color: {COLORS['main_text']}; margin-top: 6px;">Random Forest v1.0</div>
            </div>
        </div>

        <div style="background: {box_bg}; border-left: 4px solid {banner_border}; border-radius: 0 8px 8px 0; padding: 14px 18px;">
            <div style="font-size: 14px; font-weight: 700; color: {COLORS['deep_navy']}; margin-bottom: 4px;">{advisory_title}</div>
            <div style="font-size: 13px; color: {COLORS['main_text']}; line-height: 1.45;">{advisory_text}</div>
        </div>
    </div>
    """)


def render_why_flagged_accordion(payload: Dict[str, Any]):
    """
    Renders the required 'Why was this student flagged?' explanation panel.
    Transparently discloses that only global model-level permutation importance is available.
    """
    with st.expander("Why was this student flagged? — Model Signals & Feature Insights", expanded=True):
        render_html("""
        <div style="margin-bottom: 14px;">
            <div style="font-size: 13px; color: #4B5563; line-height: 1.5;">
                Below are the primary input features and their corresponding global permutation importance ranking in the 
                underlying Random Forest classifier.
            </div>
        </div>
        """)

        st.info(
            "**Model Explanation Transparency Notice:**\n\n"
            "The backend prediction service provides global permutation feature importances derived from the held-out "
            "validation dataset. Individual per-instance attributions (such as local SHAP or LIME values) are not generated "
            "by the current production API pipeline. Signals shown below reflect population-level predictive importance, "
            "not a proven causal link for this specific student."
        )

        signals_data = [
            {
                "Feature / Signal": "Course Module",
                "Submitted Value": payload.get("code_module", "—"),
                "Global Importance": "0.0905 (Rank 1)",
                "Contextual Guidance": "Course subject curriculum structure has the highest permutation weight.",
            },
            {
                "Feature / Signal": "Active Days in Last 30 Days",
                "Submitted Value": f"{payload.get('active_days_last_30_days', 0):.0f} days",
                "Global Importance": "0.0346 (Rank 2)",
                "Contextual Guidance": "Log-in frequency in the 30-day run-up strongly differentiates active learners.",
            },
            {
                "Feature / Signal": "Target Assessment Date",
                "Submitted Value": f"Day {payload.get('target_date', 0):.0f}",
                "Global Importance": "0.0340 (Rank 3)",
                "Contextual Guidance": "Position of the assessment within the semester syllabus.",
            },
            {
                "Feature / Signal": "Clicks in Last 30 Days",
                "Submitted Value": f"{payload.get('clicks_last_30_days', 0):,.0f} clicks",
                "Global Importance": "0.0288 (Rank 4)",
                "Contextual Guidance": "Recent learning material engagement volume.",
            },
            {
                "Feature / Signal": "Assessment Type",
                "Submitted Value": payload.get("target_assessment_type", "—"),
                "Global Importance": "0.0277 (Rank 5)",
                "Contextual Guidance": "TMA (tutor-marked) vs CMA (computer-marked) evaluation format.",
            },
            {
                "Feature / Signal": "Clicks in Last 14 Days",
                "Submitted Value": f"{payload.get('clicks_last_14_days', 0):,.0f} clicks",
                "Global Importance": "0.0233 (Rank 6)",
                "Contextual Guidance": "Immediate fortnightly revision and submission preparation pace.",
            },
            {
                "Feature / Signal": "Clicks in Last 7 Days",
                "Submitted Value": f"{payload.get('clicks_last_7_days', 0):,.0f} clicks",
                "Global Importance": "0.0125 (Rank 7)",
                "Contextual Guidance": "Final week activity surge or disengagement indicator.",
            },
            {
                "Feature / Signal": "Total VLE Clicks",
                "Submitted Value": f"{payload.get('total_clicks', 0):,.0f} clicks",
                "Global Importance": "0.0036 (Rank 9)",
                "Contextual Guidance": "Cumulative semester learning footprint.",
            },
        ]

        st.dataframe(
            pd.DataFrame(signals_data),
            use_container_width=True,
            hide_index=True,
        )
