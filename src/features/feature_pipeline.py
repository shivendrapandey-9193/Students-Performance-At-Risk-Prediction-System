"""
Feature engineering functions for Student Insight AI.
Computes engagement dynamics, velocity, and consistency metrics from raw VLE click history.
"""

import numpy as np
import pandas as pd


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer domain-specific academic engagement signals:
    1. click_momentum_7_30: recency-weighted activity surge or drop
    2. clicks_per_activity_record: interaction density per distinct study session
    3. consistency_last_30d: monthly participation regularness (active days / 30)
    4. engagement_density: cumulative active days relative to course elapsed days
    5. velocity_ratio: 7-day daily click rate vs 30-day daily click rate
    """
    d = df.copy()

    # 1. Click momentum (recency weighting)
    clicks_7 = d["clicks_last_7_days"].astype(float)
    clicks_30 = d["clicks_last_30_days"].astype(float)
    d["click_momentum_7_30"] = (clicks_7 * 4.0) / (clicks_30 + 1.0)

    # 2. Activity intensity (clicks per interaction record)
    total_clicks = d["total_clicks"].astype(float)
    records = d["activity_records"].astype(float)
    d["clicks_per_activity_record"] = total_clicks / (records + 1.0)

    # 3. Monthly study consistency (fraction of days active in past month, bounded [0, 1])
    active_30 = d["active_days_last_30_days"].astype(float)
    d["consistency_last_30d"] = np.clip(active_30 / 30.0, 0.0, 1.0)

    # 4. Long-term activity density (active days relative to days elapsed)
    active_total = d["active_days"].astype(float)
    target_date = d["target_date"].astype(float)
    d["engagement_density"] = active_total / np.maximum(target_date, 1.0)

    # 5. Engagement velocity ratio (7-day daily rate vs 30-day daily rate)
    rate_7d = clicks_7 / 7.0
    rate_30d = clicks_30 / 30.0
    d["velocity_ratio"] = (rate_7d + 1e-4) / (rate_30d + 1e-4)

    return d
