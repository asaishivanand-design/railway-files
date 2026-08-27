# Machine Learning Results

## Contribution

This part of the project covers synthetic railway maintenance data generation, maintenance-priority prediction, model evaluation, and integration with the constraint-aware scheduling baseline.

## Synthetic Dataset

The generator creates the following synthetic datasets:

- Assets: 500 rows
- Asset history: 2,000 rows
- Maintenance tasks: 5,000 rows
- Train movements: 10,000 rows
- Block windows: 3,000 rows
- Block requests: 5,000 rows
- Maintenance outcomes: 5,000 rows

The maintenance-task dataset contains 18 columns. The model uses 11 input features and predicts `priority_score`.

## Features

### Numeric features

- `severity`
- `criticality`
- `condition_score`
- `overdue_days`
- `failure_frequency`
- `safety_impact`
- `operational_impact`
- `estimated_duration_minutes`

### Categorical features

- `department`
- `maintenance_type`
- `defect_type`

### Target

- `priority_score`

## Models Trained

Two baseline regression models were trained:

1. Linear Regression
2. Random Forest Regressor

The dataset was split into 4,000 training rows and 1,000 testing rows.

## Model Performance

The final recorded evaluation was:

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Linear Regression | 4.803 | 6.033 | **0.892** |
| Random Forest | 5.083 | 6.382 | 0.879 |

Based on these metrics, **Linear Regression was selected as the best baseline model**.

## Feature Importance

The Random Forest evaluation showed that the strongest predictive features were:

1. Severity — 0.6232
2. Criticality — 0.1911
3. Overdue days — 0.0500
4. Condition score — 0.0430
5. Failure frequency — 0.0343
6. Safety impact — 0.0282
7. Estimated duration — 0.0183

This indicates that severity and criticality were the dominant signals in the synthetic priority data.

## Prediction

The trained models are saved under:

`ai/priority_model/models/`

The prediction script can load the selected model and produce a maintenance priority score and priority class for a sample maintenance task.

## Scheduling Integration

The predicted maintenance priorities were used by a priority-aware greedy block scheduler.

The first validated optimizer baseline produced:

| Metric | Result |
|---|---:|
| Maintenance tasks | 5,000 |
| Scheduled tasks | 1,279 |
| Scheduled ratio | 25.58% |
| Blocks used | 1,163 |
| Coordinated blocks | 83 |
| Departments represented | 3 |
| Objective score | 0.5055 |
| Validation errors | 0 |
| Validation warnings | 0 |

The validator confirmed that this schedule satisfied the implemented block and timing constraints.

## Important Limitation / Next Step

The baseline scheduler prioritizes higher-value maintenance overall, but some high-priority tasks can still remain unscheduled. For example, the analysis found an unscheduled Critical task with priority score 95.79.

This is a known limitation of the current greedy baseline and provides a clear direction for the next optimization stage: improve critical/high-priority task coverage while maintaining all hard scheduling constraints.

## Reproducibility

Install dependencies with:

```text
python -m pip install -r requirements.txt
```

Generate synthetic data:

```text
python scripts\generate_synthetic_data.py
```

Train the models:

```text
python ai\priority_model\train.py
```

Evaluate the models:

```text
python ai\priority_model\evaluate.py
```

Run a prediction example:

```text
python ai\priority_model\predict.py
```

Run the scheduling baseline:

```text
python -m optimizer.scheduler
```

## Summary

The ML pipeline provides a reproducible baseline for predicting maintenance priority from synthetic railway maintenance data. The predicted priorities are then consumed by a constraint-aware scheduling baseline, creating the foundation for comparison with more advanced optimization methods.
