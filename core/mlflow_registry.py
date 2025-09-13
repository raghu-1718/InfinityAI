import mlflow

def log_model(model, model_name):
    with mlflow.start_run():
        mlflow.sklearn.log_model(model, model_name)
        print(f"Model {model_name} logged to MLflow.")

def register_model(model_uri, model_name):
    result = mlflow.register_model(model_uri, model_name)
    print(f"Model registered: {result}")
