"""
Model evaluation and explainability.

Evaluates the trained priority models and reports:
    - MAE
    - RMSE
    - R2
    - Random Forest feature importance
"""

from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split

from features import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
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

RANDOM_FOREST_PATH = (
    MODEL_DIR
    / "random_forest.joblib"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    print()
    print("Loading dataset...")

    df = load_data()

    X, y = prepare_features(df)

    # --------------------------------------------------------
    # Same train/test split used during training
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
        )
    )

    print(
        f"Training rows: {len(X_train):,}"
    )

    print(
        f"Testing rows:  {len(X_test):,}"
    )

    # --------------------------------------------------------
    # Load Random Forest
    # --------------------------------------------------------

    print()
    print("Loading Random Forest model...")

    if not RANDOM_FOREST_PATH.exists():

        raise FileNotFoundError(
            f"Model not found: {RANDOM_FOREST_PATH}"
        )

    model = joblib.load(
        RANDOM_FOREST_PATH
    )

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    print(
        "Generating predictions..."
    )

    predictions = model.predict(
        X_test
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

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
    print("=" * 60)
    print("RANDOM FOREST PERFORMANCE")
    print("=" * 60)

    print(
        f"MAE  : {mae:.3f}"
    )

    print(
        f"RMSE : {rmse:.3f}"
    )

    print(
        f"R²   : {r2:.3f}"
    )

    # ========================================================
    # FEATURE IMPORTANCE
    # ========================================================

    print()
    print("=" * 60)
    print("FEATURE IMPORTANCE")
    print("=" * 60)

    # Get the preprocessing stage.
    preprocessor = model.named_steps[
        "preprocessor"
    ]

    # Get the Random Forest itself.
    random_forest = model.named_steps[
        "model"
    ]

    # Get names after one-hot encoding.
    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    importances = (
        random_forest
        .feature_importances_
    )

    importance_df = pd.DataFrame({

        "feature":
            feature_names,

        "importance":
            importances,

    })

    importance_df = (
        importance_df
        .sort_values(
            "importance",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    print()

    for index, row in (
        importance_df
        .head(15)
        .iterrows()
    ):

        print(
            f"{index + 1:2d}. "
            f"{row['feature']:<45}"
            f"{row['importance']:.4f}"
        )

    # ========================================================
    # PREDICTION EXAMPLES
    # ========================================================

    print()
    print("=" * 60)
    print("SAMPLE PREDICTIONS")
    print("=" * 60)

    comparison = pd.DataFrame({

        "actual":
            y_test.values,

        "predicted":
            predictions,

    })

    comparison["error"] = (
        comparison["predicted"]
        - comparison["actual"]
    )

    print()

    print(
        comparison
        .head(10)
        .round(2)
        .to_string(
            index=False
        )
    )

    print()
    print("=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()