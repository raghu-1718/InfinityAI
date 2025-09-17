
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
import numpy as np

mlflow.set_tracking_uri("https://www.infinityai.pro/mlflow")  # MLflow server

def train_and_log_model(X, y, model_name: str = "random_forest_model", params: dict = None):
	"""Train a model, log to MLflow, and register it."""
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
	model = RandomForestClassifier(**(params or {}))
	model.fit(X_train, y_train)
	acc = accuracy_score(y_test, model.predict(X_test))
	with mlflow.start_run() as run:
		mlflow.sklearn.log_model(model, model_name)
		mlflow.log_metric("accuracy", acc)
		mlflow.log_params(params or {})
		run_id = run.info.run_id
	client = mlflow.tracking.MlflowClient()
	model_uri = f"runs:/{run_id}/{model_name}"
	try:
		client.create_registered_model(model_name)
	except Exception:
		pass  # Already exists
	client.create_model_version(model_name, model_uri, "production")
	return {"run_id": run_id, "accuracy": acc, "model_uri": model_uri}

def predict_with_model(model_uri: str, X: np.ndarray):
	"""Load a model from MLflow and predict."""
	model = mlflow.sklearn.load_model(model_uri)
	preds = model.predict(X)
	return preds.tolist()

def monitor_drift(reference_data: np.ndarray, current_data: np.ndarray, output_html: str = None):
	"""Run data drift detection and optionally save report."""
	report = Report(metrics=[DataDriftPreset()])
	report.run(reference_data=reference_data, current_data=current_data)
	if output_html:
		report.save_html(output_html)
	return report.as_dict()

def list_registered_models():
	client = mlflow.tracking.MlflowClient()
	return [m.name for m in client.list_registered_models()]

def get_model_versions(model_name: str):
	client = mlflow.tracking.MlflowClient()
	return client.get_latest_versions(model_name)
