"""
Feature engineering for the maintenance priority model.
"""

from pathlib import Path

import pandas as pd


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "synthetic"
    / "maintenance_tasks.csv"
)


TARGET = "priority_score"


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


def load_data(path=DATA_PATH):
    """Load the synthetic maintenance dataset."""
    return pd.read_csv(path)


def prepare_features(df):
    """
    Convert raw maintenance records into ML features.

    Returns:
        X: model input features
        y: target priority score
    """

    required_columns = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
        + [TARGET]
    )

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    X = df[
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    ].copy()

    y = df[TARGET].copy()

    return X, y


if __name__ == "__main__":

    df = load_data()

    X, y = prepare_features(df)

    print("Dataset shape:", df.shape)
    print("Feature shape:", X.shape)
    print("Target shape:", y.shape)

    print()
    print("Numeric features:")

    for feature in NUMERIC_FEATURES:
        print("  -", feature)

    print()
    print("Categorical features:")

    for feature in CATEGORICAL_FEATURES:
        print("  -", feature)

    print()
    print("Target:", TARGET)