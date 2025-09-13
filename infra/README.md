# Infrastructure Automation

## Terraform
- `main.tf`: Azure Container App provisioning

## Monitoring
- `prometheus.yml`: Prometheus scrape config for FastAPI
- `grafana-provisioning.yml`: Grafana datasource config for Prometheus

## Usage
- Deploy infrastructure: `terraform init && terraform apply`
- Start Prometheus: `prometheus --config.file=infra/prometheus.yml`
- Start Grafana: `grafana-server --config=infra/grafana-provisioning.yml`
