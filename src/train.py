import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
import json
import joblib
import os
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

EVAL_THRESHOLD = 0.70
FEATURE_COLUMNS = [
    "fixed_acidity", "volatile_acidity", "citric_acid", "residual_sugar",
    "chlorides", "free_sulfur_dioxide", "total_sulfur_dioxide", "density",
    "pH", "sulphates", "alcohol", "wine_type",
]


def _build_model(params: dict):
    model_type = params.get("model_type", "random_forest")

    if model_type == "random_forest":
        model_params = {
            "n_estimators": params.get("n_estimators", 100),
            "max_depth": params.get("max_depth"),
            "min_samples_split": params.get("min_samples_split", 2),
            "random_state": 42,
        }
        return RandomForestClassifier(**model_params)

    if model_type == "extra_trees":
        model_params = {
            "n_estimators": params.get("n_estimators", 100),
            "max_depth": params.get("max_depth"),
            "min_samples_split": params.get("min_samples_split", 2),
            "random_state": 42,
            "n_jobs": params.get("n_jobs", -1),
        }
        return ExtraTreesClassifier(**model_params)

    if model_type == "gradient_boosting":
        max_depth = params.get("max_depth")
        model_params = {
            "n_estimators": params.get("n_estimators", 100),
            "max_depth": 3 if max_depth is None else max_depth,
            "learning_rate": params.get("learning_rate", 0.1),
            "random_state": 42,
        }
        return GradientBoostingClassifier(**model_params)

    if model_type == "logistic_regression":
        model_params = {
            "C": params.get("C", 1.0),
            "max_iter": params.get("max_iter", 1000),
            "random_state": 42,
        }
        return make_pipeline(
            StandardScaler(),
            LogisticRegression(**model_params),
        )

    raise ValueError(
        "model_type must be one of: random_forest, extra_trees, "
        "gradient_boosting, logistic_regression"
    )


def _label_distribution(y_train: pd.Series) -> dict[str, float]:
    distribution = y_train.value_counts(normalize=True).sort_index()
    return {str(label): float(distribution.get(label, 0.0)) for label in [0, 1, 2]}


def _write_report(y_eval, preds, metrics_by_class: dict) -> None:
    matrix = confusion_matrix(y_eval, preds, labels=[0, 1, 2])
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/report.txt", "w", encoding="utf-8") as f:
        f.write("Confusion matrix (rows=true, cols=predicted; labels 0,1,2)\n")
        f.write(str(matrix))
        f.write("\n\nPrecision/recall per class\n")
        for label in ["0", "1", "2"]:
            values = metrics_by_class[label]
            f.write(
                f"class {label}: precision={values['precision']:.4f}, "
                f"recall={values['recall']:.4f}\n"
            )
        f.write("\nFull classification report\n")
        f.write(classification_report(y_eval, preds, labels=[0, 1, 2], zero_division=0))


def train(
    params: dict,
    data_path: str = "data/train_phase1.csv",
    eval_path: str = "data/eval.csv",
) -> float:
    """
    Huan luyen mo hinh va ghi nhan ket qua vao MLflow.

    Tham so:
        params     : dict chua cac sieu tham so cho RandomForestClassifier.
        data_path  : duong dan den file du lieu huan luyen.
        eval_path  : duong dan den file du lieu danh gia.

    Tra ve:
        accuracy (float): do chinh xac tren tap danh gia.
    """

    df_train = pd.read_csv(data_path)
    df_eval = pd.read_csv(eval_path)

    X_train = df_train.drop(columns=["target"])
    y_train = df_train["target"]
    X_eval = df_eval.drop(columns=["target"])
    y_eval = df_eval["target"]

    if not os.environ.get("MLFLOW_TRACKING_URI"):
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment(os.environ.get("MLFLOW_EXPERIMENT_NAME", "wine-quality"))

    with mlflow.start_run():

        mlflow.log_params(params)

        model = _build_model(params)
        model.fit(X_train, y_train)

        preds = model.predict(X_eval)
        acc = accuracy_score(y_eval, preds)
        f1 = f1_score(y_eval, preds, average="weighted")
        precision, recall, _, _ = precision_recall_fscore_support(
            y_eval,
            preds,
            labels=[0, 1, 2],
            zero_division=0,
        )
        per_class = {
            str(label): {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
            }
            for index, label in enumerate([0, 1, 2])
        }
        label_distribution = _label_distribution(y_train)
        drift_warnings = [
            f"class {label} is {ratio:.2%} of training data (< 10%)"
            for label, ratio in label_distribution.items()
            if ratio < 0.10
        ]

        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        for label in ["0", "1", "2"]:
            mlflow.log_metric(f"precision_class_{label}", per_class[label]["precision"])
            mlflow.log_metric(f"recall_class_{label}", per_class[label]["recall"])
            mlflow.log_metric(
                f"train_label_ratio_class_{label}",
                label_distribution[label],
            )
        mlflow.sklearn.log_model(model, "model")

        print(f"Model type: {params.get('model_type', 'random_forest')}")
        print(f"Accuracy: {acc:.4f} | F1: {f1:.4f}")
        print(f"Train label distribution: {label_distribution}")
        if drift_warnings:
            print("DATA DRIFT WARNING:")
            for warning in drift_warnings:
                print(f"- {warning}")

        os.makedirs("outputs", exist_ok=True)
        metrics = {
            "model_type": params.get("model_type", "random_forest"),
            "accuracy": float(acc),
            "f1_score": float(f1),
            "precision_recall_by_class": per_class,
            "train_label_distribution": label_distribution,
            "data_drift_warnings": drift_warnings,
        }
        with open("outputs/metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        _write_report(y_eval, preds, per_class)
        mlflow.log_artifact("outputs/report.txt")

        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.pkl")

    return float(acc)


if __name__ == "__main__":
    with open("params.yaml") as f:
        params = yaml.safe_load(f)
    train(params)
