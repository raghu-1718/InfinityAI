# MLflow model management example
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Train and log model
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier()
model.fit(X_train, y_train)

mlflow.set_tracking_uri("http://localhost:5000")  # MLflow server
mlflow.sklearn.log_model(model, "random_forest_model")
mlflow.log_metric("accuracy", model.score(X_test, y_test))

# Model registry and deployment
client = mlflow.tracking.MlflowClient()
model_uri = "runs:/{}/random_forest_model".format(mlflow.active_run().info.run_id)
client.create_registered_model("RandomForestClassifier")
client.create_model_version("RandomForestClassifier", model_uri, "production")

# Monitoring and drift detection (Evidently)
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=X_train, current_data=X_test)
report.save_html("drift_report.html")
