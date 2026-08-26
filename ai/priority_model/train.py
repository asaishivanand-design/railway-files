"""
Train the maintenance priority model.

Models:
    1. Linear Regression baseline
    2. Random Forest Regressor

Target:
    priority_score (0-100)
"""

from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from features import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    TARGET,
    load_data,
    prepare_features,
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20

MODEL_DIR = (
    Path(__file__).resolve().parent
    / "models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# METRICS
# ============================================================

def evaluate_model(
    model,
    X_test,
    y_test,
    model_name,
):
    """Evaluate a trained regression model."""

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = mean_squared_error(
        y_test,
        predictions,
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions,
    )

    print()
    print("=" * 55)
    print(model_name)
    print("=" * 55)

    print(
        f"MAE  : {mae:.3f}"
    )

    print(
        f"RMSE : {rmse:.3f}"
    )

    print(
        f"R²   : {r2:.3f}"
    )

    return {
        "model": model_name,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 55)
    print("MAINTENANCE PRIORITY MODEL TRAINING")
    print("=" * 55)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    print()
    print("Loading dataset...")

    df = load_data()

    print(
        f"Dataset rows: {len(df):,}"
    )

    # --------------------------------------------------------
    # Prepare features
    # --------------------------------------------------------

    X, y = prepare_features(df)

    print(
        f"Features: {X.shape[1]}"
    )

    print(
        f"Target: {TARGET}"
    )

    # --------------------------------------------------------
    # Train/test split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
        )
    )

    print()
    print(
        f"Training rows: {len(X_train):,}"
    )

    print(
        f"Testing rows:  {len(X_test):,}"
    )

    # ========================================================
    # PREPROCESSING
    # ========================================================

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                "passthrough",
                NUMERIC_FEATURES,
            ),

            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                ),
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    # ========================================================
    # MODEL 1 — LINEAR REGRESSION
    # ========================================================

    linear_model = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),

            (
                "model",
                LinearRegression(),
            ),
        ]
    )

    print()
    print(
        "Training Linear Regression..."
    )

    linear_model.fit(
        X_train,
        y_train,
    )

    linear_results = evaluate_model(
        linear_model,
        X_test,
        y_test,
        "Linear Regression",
    )

    # ========================================================
    # MODEL 2 — RANDOM FOREST
    # ========================================================

    random_forest_model = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),

            (
                "model",
                RandomForestRegressor(
                    n_estimators=300,
                    max_depth=12,
                    min_samples_leaf=3,
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    print()
    print(
        "Training Random Forest..."
    )

    random_forest_model.fit(
        X_train,
        y_train,
    )

    rf_results = evaluate_model(
        random_forest_model,
        X_test,
        y_test,
        "Random Forest",
    )

    # ========================================================
    # SELECT BEST MODEL
    # ========================================================

    results = [
        linear_results,
        rf_results,
    ]

    best_result = min(
        results,
        key=lambda result: result["mae"],
    )

    print()
    print("=" * 55)
    print("MODEL COMPARISON")
    print("=" * 55)

    for result in results:

        print(
            f"{result['model']:<20}"
            f" MAE={result['mae']:.3f}"
            f" RMSE={result['rmse']:.3f}"
            f" R²={result['r2']:.3f}"
        )

    print()
    print(
        f"Best model: {best_result['model']}"
    )

    # ========================================================
    # SAVE MODELS
    # ========================================================

    linear_path = (
        MODEL_DIR
        / "linear_regression.joblib"
    )

    rf_path = (
        MODEL_DIR
        / "random_forest.joblib"
    )

    joblib.dump(
        linear_model,
        linear_path,
    )

    joblib.dump(
        random_forest_model,
        rf_path,
    )

    print()
    print(
        f"Saved: {linear_path}"
    )

    print(
        f"Saved: {rf_path}"
    )

    print()
    print("=" * 55)
    print("TRAINING COMPLETE")
    print("=" * 55)


if __name__ == "__main__":
    main()