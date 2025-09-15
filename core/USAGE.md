# InfinityAI Usage Guide

## 1. Extensibility (Plugins)
- Place plugins in `core/extensibility_plugins/`
- Run `python core/test_extensibility.py` to discover and execute plugins

## 2. Infrastructure & Monitoring
- Terraform: `cd infra && terraform init && terraform apply`
- Prometheus: `prometheus --config.file=infra/prometheus.yml`
- Grafana: `grafana-server --config=infra/grafana-provisioning.yml`

## 3. Airflow ETL
- DAG file: `core/airflow_etl_dag.py`
- Start Airflow: `airflow standalone` (after installing Airflow)
- Place DAG in Airflow DAGs folder

## 4. MLflow Model Registry
- Script: `core/mlflow_registry.py`
- Start MLflow UI: `mlflow ui`
- Use provided functions to log and register models

## 5. Security Scans
- Trivy: `python core/security_scan.py` (edit image name as needed)
- Snyk: `python core/security_scan.py` (edit path as needed)

## 6. CI/CD
- GitHub Actions workflow: `.github/workflows/ci-cd.yml`
- Push to main branch to trigger build, test, Docker push, and Azure deploy

---

## Requirements
- Python 3.12.x (recommended)
- Docker, Terraform, Prometheus, Grafana, Airflow, MLflow, Trivy, Snyk installed

## Quickstart
1. Set up Python 3.12 and create a new venv
2. Install dependencies: `pip install -r requirements.txt`
3. Follow steps above for each tool
