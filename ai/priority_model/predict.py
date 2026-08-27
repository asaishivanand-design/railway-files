"""
Prediction interface for the maintenance priority model.

The currently selected production model is Linear Regression,
based on the Experiment 2 validation results.
"""

from pathlib import Path

import joblib
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "linear_regression.joblib"
)


NUMERIC_FEATURES = [
    "severity",
    "criticality",
    "condition_score",
    "overdue_days",
    "failure_frequency",
    "safety_impact",
    "operational_impact",
    "estimated_duration_minutes",
]


CATEGORICAL_FEATURES = [
    "department",
    "maintenance_type",
    "defect_type",
]


# ============================================================
# MODEL
# ============================================================

def load_model():
    """Load the selected trained model."""

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    return joblib.load(
        MODEL_PATH
    )


# ============================================================
# PRIORITY CLASS
# ============================================================

def classify_priority(score):
    """Convert numeric priority score to priority class."""

    if score >= 80:

        return "CRITICAL"

    if score >= 60:

        return "HIGH"

    if score >= 40:

        return "MEDIUM"

    return "LOW"


# ============================================================
# PREDICTION
# ============================================================

def predict_priority(task):
    """
    Predict maintenance priority.

    Parameters
    ----------
    task : dict
        Maintenance task containing the required model features.

    Returns
    -------
    dict
        Priority score and priority class.
    """

    required_features = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    )

    missing_features = [
        feature
        for feature in required_features
        if feature not in task
    ]

    if missing_features:

        raise ValueError(
            "Missing features: "
            + ", ".join(
                missing_features
            )
        )

    model = load_model()

    row = pd.DataFrame([
        task
    ])

    prediction = model.predict(
        row
    )[0]

    score = float(
        prediction
    )

    score = max(
        0.0,
        min(
            100.0,
            score,
        ),
    )

    return {

        "priority_score":
            round(
                score,
                2,
            ),

        "priority_class":
            classify_priority(
                score
            ),

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    sample_task = {

        "severity": 5,

        "criticality": 5,

        "condition_score": 0.35,

        "overdue_days": 25,

        "failure_frequency": 2.1,

        "safety_impact": 0.90,

        "operational_impact": 0.85,

        "estimated_duration_minutes": 120,

        "department": "ENGINEERING",

        "maintenance_type": "CORRECTIVE",

        "defect_type": "RAIL_CRACK",

    }

    result = predict_priority(
        sample_task
    )

    print(
        "Selected model:"
    )

    print(
        "  Linear Regression"
    )

    print()

    print(
        "Sample maintenance task:"
    )

    print(
        f"  priority_score: "
        f"{result['priority_score']}"
    )

    print(
        f"  priority_class: "
        f"{result['priority_class']}"
    )