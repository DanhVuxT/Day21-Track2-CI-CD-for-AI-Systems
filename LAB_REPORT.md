# Lab report

## Best hyperparameters

Final selected configuration:

```yaml
model_type: extra_trees
n_estimators: 800
max_depth:
min_samples_split: 2
n_jobs: -1
```

Local evidence after adding `train_phase2.csv` into `train_phase1.csv`:

- Accuracy: `0.7660`
- F1 score: `0.7651`
- Training label distribution: class 0 `36.86%`, class 1 `43.51%`, class 2 `19.63%`
- Data drift warnings: none, because every class is above `10%`

This configuration was selected because it gave the best verified held-out
accuracy after the continuous-training data update. Before adding the new data,
the best local run was below the `0.70` deployment gate, so the step 3 data
update is necessary to pass the gate honestly.

## CI/CD and cloud setup

The project is configured for AWS like the reference implementation:

- DVC remote: S3 bucket under `s3://<bucket>/dvc`
- Serving VM: AWS EC2 running FastAPI with systemd
- Model artifact: `s3://<bucket>/models/latest/model.pkl`
- Metrics/report artifacts: `s3://<bucket>/metrics/latest/`
- GitHub Actions jobs: `Unit Test`, `Train`, `Eval`, `Deploy`

Screenshots must be captured manually from MLflow UI, GitHub Actions, AWS S3,
AWS EC2/curl output, and optional DagsHub. The exact commands and web pages are
listed in `SUBMISSION_COMMANDS.md`.

## Bonus implemented

- DagsHub/remote MLflow support through optional GitHub secrets:
  `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`, `MLFLOW_TRACKING_PASSWORD`.
- Multiple algorithms in `src/train.py`: RandomForest, ExtraTrees,
  GradientBoosting, LogisticRegression.
- Automatic `outputs/report.txt` with confusion matrix, precision, and recall.
- Deployment rollback guard in GitHub Actions: compare new accuracy with
  `metrics/latest/metrics.json` from S3 and cancel deploy if worse.
- Data drift check: label distribution is written to `outputs/metrics.json`, and
  classes below `10%` are printed as warnings.

## Issues and fixes

- `mlflow==2.13.0` imports `pkg_resources`; modern `setuptools` removed it, so
  `setuptools<81` is pinned for reproducible local and CI installs.
- Cloud steps require real AWS credentials, S3 bucket, EC2 IP, and GitHub
  secrets. Those values are intentionally not committed to git.
