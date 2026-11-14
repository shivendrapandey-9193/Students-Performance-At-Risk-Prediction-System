"""
API Client for communicating with the Student At-Risk Prediction FastAPI backend.
Preserves strict backend integration, implements centralized URL resolution,
and supports both single and high-performance batch prediction endpoints.
"""

import os
import time
import requests
import pandas as pd
from typing import Dict, Any, Tuple, Optional, Callable, List


def get_api_base_url() -> str:
    """
    Centralized API URL resolution adhering strictly to deployment priority:
    1. Streamlit secrets (for Streamlit Community Cloud)
    2. Environment variables (API_BASE_URL or API_URL for containers / PaaS)
    3. Localhost fallback (only for local development)
    """
    configured_url = None
    try:
        import streamlit as st
        configured_url = st.secrets.get("API_BASE_URL") or st.secrets.get("API_URL")
    except Exception:
        configured_url = None

    if not configured_url:
        configured_url = os.getenv("API_BASE_URL") or os.getenv("API_URL")

    if configured_url:
        return str(configured_url).rstrip("/")

    return "http://127.0.0.1:8000"


DEFAULT_API_URL = get_api_base_url()

REQUIRED_BATCH_COLUMNS = [
    "code_module",
    "code_presentation",
    "target_assessment_type",
    "target_date",
    "total_clicks",
    "activity_records",
    "active_days",
    "active_days_last_30_days",
    "clicks_last_7_days",
    "clicks_last_14_days",
    "clicks_last_30_days",
    "average_clicks_per_active_day",
]


def check_api_health(api_url: Optional[str] = None, timeout: float = 3.5) -> Dict[str, Any]:
    """
    Check backend connection and health status. Measures live round-trip latency.
    """
    base_url = api_url or get_api_base_url()
    t0 = time.perf_counter()
    try:
        response = requests.get(f"{base_url}/health", timeout=timeout)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)

        if response.status_code == 200:
            data = response.json()
            return {
                "connected": True,
                "status": data.get("status", "healthy"),
                "model_loaded": bool(data.get("model_loaded")),
                "model": data.get("model", "Random Forest - Recall Focused"),
                "threshold": float(data.get("threshold", 0.24567134268537077)),
                "latency_ms": latency_ms,
                "error": None,
                "raw_response": data,
                "api_url": base_url,
            }
        else:
            return {
                "connected": False,
                "status": f"HTTP {response.status_code}",
                "model_loaded": False,
                "model": "Unknown",
                "threshold": None,
                "latency_ms": latency_ms,
                "error": f"API returned non-200 status code: {response.text}",
                "raw_response": None,
                "api_url": base_url,
            }
    except requests.exceptions.ConnectionError:
        return {
            "connected": False,
            "status": "offline",
            "model_loaded": False,
            "model": "Unavailable",
            "threshold": None,
            "latency_ms": 0.0,
            "error": f"Connection refused. The backend is not reachable at {base_url}",
            "raw_response": None,
            "api_url": base_url,
        }
    except requests.exceptions.Timeout:
        return {
            "connected": False,
            "status": "timeout",
            "model_loaded": False,
            "model": "Unavailable",
            "threshold": None,
            "latency_ms": 0.0,
            "error": f"Health check timed out after {timeout}s at {base_url}",
            "raw_response": None,
            "api_url": base_url,
        }
    except Exception as exc:
        return {
            "connected": False,
            "status": "error",
            "model_loaded": False,
            "model": "Unavailable",
            "threshold": None,
            "latency_ms": 0.0,
            "error": str(exc),
            "raw_response": None,
            "api_url": base_url,
        }


def predict_student_risk(
    payload: Dict[str, Any],
    api_url: Optional[str] = None,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    """
    Send a single student's features to POST /predict.
    Validates that real backend prediction is executed.
    """
    base_url = api_url or get_api_base_url()
    t0 = time.perf_counter()
    try:
        response = requests.post(f"{base_url}/predict", json=payload, timeout=timeout)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "status_code": 200,
                "data": data,
                "latency_ms": latency_ms,
                "error": None,
            }
        elif response.status_code == 422:
            return {
                "success": False,
                "status_code": 422,
                "data": None,
                "latency_ms": latency_ms,
                "error": f"Validation Error (422): {response.text}",
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "data": None,
                "latency_ms": latency_ms,
                "error": f"Server Error ({response.status_code}): {response.text}",
            }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "status_code": 0,
            "data": None,
            "latency_ms": 0.0,
            "error": f"Cannot reach prediction API at {base_url}. Verify backend service is online.",
        }
    except Exception as exc:
        return {
            "success": False,
            "status_code": 0,
            "data": None,
            "latency_ms": 0.0,
            "error": f"Prediction request failed: {str(exc)}",
        }


def validate_batch_dataframe(df: pd.DataFrame) -> Tuple[bool, Optional[str], pd.DataFrame]:
    """
    Validates that the provided dataframe has all required columns and valid types.
    """
    missing = [c for c in REQUIRED_BATCH_COLUMNS if c not in df.columns]
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}", df

    clean_df = df[REQUIRED_BATCH_COLUMNS].copy()

    # Coerce numeric columns
    numeric_cols = [
        "target_date", "total_clicks", "activity_records", "active_days",
        "active_days_last_30_days", "clicks_last_7_days", "clicks_last_14_days",
        "clicks_last_30_days", "average_clicks_per_active_day"
    ]
    for col in numeric_cols:
        clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce").fillna(0.0)

    # Coerce string columns
    for col in ["code_module", "code_presentation", "target_assessment_type"]:
        clean_df[col] = clean_df[col].astype(str).str.strip()

    return True, None, clean_df


def predict_batch_records(
    df: pd.DataFrame,
    api_url: Optional[str] = None,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    max_records: int = 500,
) -> Dict[str, Any]:
    """
    Predict a cohort of student records by sending them to the genuine backend.
    Tries the high-performance POST /predict/batch endpoint first; falls back to
    iterative POST /predict if batch endpoint is unavailable.
    """
    base_url = api_url or get_api_base_url()
    valid, err_msg, clean_df = validate_batch_dataframe(df)
    if not valid:
        return {"success": False, "error": err_msg, "results_df": None, "summary": {}}

    total_records = min(len(clean_df), max_records)
    records_to_process = clean_df.iloc[:total_records]

    # Clean and enforce monotonicity
    payload_list: List[Dict[str, Any]] = []
    for _, row in records_to_process.iterrows():
        p = {
            "code_module": str(row["code_module"]),
            "code_presentation": str(row["code_presentation"]),
            "target_assessment_type": str(row["target_assessment_type"]),
            "target_date": float(row["target_date"]),
            "total_clicks": float(row["total_clicks"]),
            "activity_records": float(row["activity_records"]),
            "active_days": float(row["active_days"]),
            "active_days_last_30_days": min(float(row["active_days_last_30_days"]), 30.0),
            "clicks_last_7_days": float(row["clicks_last_7_days"]),
            "clicks_last_14_days": float(row["clicks_last_14_days"]),
            "clicks_last_30_days": float(row["clicks_last_30_days"]),
            "average_clicks_per_active_day": float(row["average_clicks_per_active_day"]),
        }
        if p["clicks_last_7_days"] > p["clicks_last_14_days"]:
            p["clicks_last_14_days"] = p["clicks_last_7_days"]
        if p["clicks_last_14_days"] > p["clicks_last_30_days"]:
            p["clicks_last_30_days"] = p["clicks_last_14_days"]
        if p["clicks_last_30_days"] > p["total_clicks"]:
            p["total_clicks"] = p["clicks_last_30_days"]
        if p["active_days_last_30_days"] > p["active_days"]:
            p["active_days"] = p["active_days_last_30_days"]
        payload_list.append(p)

    t0 = time.perf_counter()

    # Attempt 1: Fast Vectorized Endpoint (POST /predict/batch)
    try:
        if progress_callback:
            progress_callback(0.1, f"Sending {total_records} records to batch inference endpoint...")

        resp = requests.post(
            f"{base_url}/predict/batch",
            json={"students": payload_list},
            timeout=25.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            predictions = data.get("predictions", [])
            results = []
            for idx, (p_req, p_res) in enumerate(zip(payload_list, predictions)):
                prob = float(p_res["predicted_probability"])
                flagged = bool(p_res["flagged_for_review"])
                results.append({
                    "Record #": idx + 1,
                    "Module": p_req["code_module"],
                    "Presentation": p_req["code_presentation"],
                    "Assessment": p_req["target_assessment_type"],
                    "Days to Due": p_req["target_date"],
                    "Total Clicks": int(p_req["total_clicks"]),
                    "Active Days (30d)": int(p_req["active_days_last_30_days"]),
                    "Clicks (30d)": int(p_req["clicks_last_30_days"]),
                    "Predicted Risk": prob,
                    "Risk %": f"{prob:.1%}",
                    "Review Priority": "Elevated Review Recommended" if flagged else "Below Review Threshold",
                    "Flagged": flagged,
                })

            total_time = round(time.perf_counter() - t0, 3)
            results_df = pd.DataFrame(results)
            flagged_count = int(data.get("flagged_count", 0))
            safe_count = int(data.get("safe_count", 0))
            mean_prob = float(results_df["Predicted Risk"].mean()) if not results_df.empty else 0.0

            if progress_callback:
                progress_callback(1.0, f"Completed {total_records} records in {total_time}s!")

            return {
                "success": True,
                "error": None,
                "results_df": results_df,
                "summary": {
                    "total_processed": len(results_df),
                    "failed_rows": 0,
                    "flagged_count": flagged_count,
                    "flagged_percentage": round((flagged_count / max(len(results_df), 1)) * 100, 1),
                    "safe_count": safe_count,
                    "mean_risk_probability": round(mean_prob * 100, 2),
                    "total_inference_time_sec": total_time,
                    "records_per_second": round(len(results_df) / max(total_time, 0.001), 1),
                },
            }
    except Exception:
        # Fall back to row-by-row
        pass

    # Attempt 2: Row-by-Row Fallback (POST /predict)
    results = []
    failed_rows = 0

    for idx, payload in enumerate(payload_list):
        pred_res = predict_student_risk(payload, api_url=base_url)

        if pred_res["success"]:
            data = pred_res["data"]
            prob = float(data["predicted_probability"])
            flagged = bool(data["flagged_for_review"])
            results.append({
                "Record #": idx + 1,
                "Module": payload["code_module"],
                "Presentation": payload["code_presentation"],
                "Assessment": payload["target_assessment_type"],
                "Days to Due": payload["target_date"],
                "Total Clicks": int(payload["total_clicks"]),
                "Active Days (30d)": int(payload["active_days_last_30_days"]),
                "Clicks (30d)": int(payload["clicks_last_30_days"]),
                "Predicted Risk": prob,
                "Risk %": f"{prob:.1%}",
                "Review Priority": "Elevated Review Recommended" if flagged else "Below Review Threshold",
                "Flagged": flagged,
            })
        else:
            failed_rows += 1

        if progress_callback:
            progress = (idx + 1) / total_records
            progress_callback(progress, f"Processed {idx + 1} of {total_records} records...")

    total_time = round(time.perf_counter() - t0, 2)
    results_df = pd.DataFrame(results)

    if results_df.empty:
        return {
            "success": False,
            "error": f"All batch prediction requests failed. Verify that FastAPI is reachable at {base_url}",
            "results_df": None,
            "summary": {},
        }

    flagged_count = int(results_df["Flagged"].sum())
    safe_count = len(results_df) - flagged_count
    mean_prob = float(results_df["Predicted Risk"].mean())

    summary = {
        "total_processed": len(results_df),
        "failed_rows": failed_rows,
        "flagged_count": flagged_count,
        "flagged_percentage": round((flagged_count / len(results_df)) * 100, 1),
        "safe_count": safe_count,
        "mean_risk_probability": round(mean_prob * 100, 2),
        "total_inference_time_sec": total_time,
        "records_per_second": round(len(results_df) / max(total_time, 0.01), 1),
    }

    return {
        "success": True,
        "error": None,
        "results_df": results_df,
        "summary": summary,
    }
