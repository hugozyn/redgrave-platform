RED-401 — Hugo van Zuylen

Local interface: http://localhost:8081
First repair the supplied dbt image (its project files are missing):
docker build -t redgrave-dbt:1.0.0-fixed dbt
Start: cd airflow && docker compose up -d --build
Stop: cd airflow && docker compose down
The local .env and terraform.tfvars files are excluded from Git.
The RSA private key is mounted read-only at runtime, outside this repository.

Terraform: cd terraform && terraform init && terraform validate && terraform plan
Do not run terraform destroy before grading.

Check final DAG (from repository root):
docker run --rm --env-file airflow/.env -v "$PWD:/lab:ro" -w /lab redgrave-airflow:1.0.0 python tests/check_dag.py

The original lab images are provided separately and must not be committed.

The dbt/ folder restores the course project missing from the supplied redgrave-dbt image.
It uses the same six models and records results with runtime=airflow.
PYTHONUSERBASE in Compose also makes the Airflow CLI available through docker compose exec.

Backfill with an explicit inclusive end-of-day timestamp:
docker compose exec airflow airflow backfill create --dag-id redgrave_daily --from-date 2026-08-02T00:00:00+01:00 --to-date 2026-08-08T23:59:59+01:00 --max-active-runs 1
The bare end date 2026-08-08 stops at midnight and omits that day's 06:00 run.

