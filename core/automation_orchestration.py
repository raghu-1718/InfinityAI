# Automation & Orchestration Example
# Automated retraining and hyperparameter tuning (Optuna)
import optuna
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

def objective(trial):
    n_estimators = trial.suggest_int('n_estimators', 10, 100)
    max_depth = trial.suggest_int('max_depth', 2, 10)
    clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
    clf.fit(X_train, y_train)
    return clf.score(X_test, y_test)

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=20)
print('Best hyperparameters:', study.best_params)

# Workflow orchestration (Prefect)
from prefect import flow, task

@task
def extract():
    print('Extracting data...')

@task
def train():
    print('Training model...')

@flow
def etl_flow():
    extract()
    train()

etl_flow()

# Event-driven triggers (serverless)
# Example: Azure Function or AWS Lambda to trigger retraining on new data arrival
