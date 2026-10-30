"""AFC Redgrave · daily pipeline.

ingest_orders  ->  dbt_build  ->  publish_daily_sales

Every task is a Docker container built in the Docker lab: Airflow only decides
WHEN and IN WHAT ORDER they run, retries them and alerts on failure.
"""
import os

import pendulum
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.sdk import DAG
from docker.types import Mount

# Folder on YOUR computer that contains rsa_key.p8 (set in docker-compose.yml).
KEYS_DIR = os.environ["REDGRAVE_KEYS_DIR"]

SNOWFLAKE_ENV = {
    "SNOWFLAKE_ACCOUNT": os.environ["SNOWFLAKE_ACCOUNT"],
    "SNOWFLAKE_USER": os.environ["SNOWFLAKE_USER"],
    "SNOWFLAKE_PRIVATE_KEY_FILE": "/secrets/rsa_key.p8",
    "REDGRAVE_RUNTIME": "airflow",   # recorded in REDGRAVE.LAB.DBT_RESULTS
}
# The key is mounted read-only at run time: it is never inside an image.
KEY_MOUNT = [Mount(source=KEYS_DIR, target="/secrets", type="bind", read_only=True)]


def alert_on_failure(context):
    """Failure alerting. Here: a loud log line. Real life: Slack / Teams / e-mail webhook."""
    ti = context["task_instance"]
    print(f"ALERT >>> task {ti.task_id} FAILED for {context['ds']} (attempt {ti.try_number}). Log: {ti.log_url}")


default_args = {
    "retries": 2,
    "retry_delay": pendulum.duration(seconds=20),
    "on_failure_callback": alert_on_failure,
}

with DAG(
    dag_id="redgrave_daily",
    # 06:00 London time every day, summer and winter (the time zone handles the clock change)
    schedule="0 6 * * *",
    start_date=pendulum.datetime(2026, 8, 1, tz="Europe/London"),
    catchup=False,
    max_active_runs=1,       # one day at a time: backfilled days never run dbt in parallel
    default_args=default_args,
    tags=["redgrave"],
) as dag:

    ingest_orders = DockerOperator(
        task_id="ingest_orders",
        image="redgrave-ingest:1.0.0",
        command="python incremental_orders.py",
        environment={**SNOWFLAKE_ENV, "PGUSER": os.environ.get("PGUSER", ""), "PGPASSWORD": os.environ.get("PGPASSWORD", "")},
        mounts=KEY_MOUNT,
        mount_tmp_dir=False,
        auto_remove="success",
    )

    dbt_build = DockerOperator(
        task_id="dbt_build",
        image="redgrave-dbt:1.0.0-fixed",
        command="dbt build",
        environment=SNOWFLAKE_ENV,
        mounts=KEY_MOUNT,
        mount_tmp_dir=False,
        auto_remove="success",
    )

    # The 06:00 run of day D publishes day D-1 (a day must be over before it is published).
    # The date comes from the run ({{ ds }}), never from "today": this is what makes backfills work.
    # --crash-on-try 1 simulates a crash after the write on the first attempt (lab step A3).
    publish_daily_sales = DockerOperator(
        task_id="publish_daily_sales",
        image="redgrave-ingest:1.0.0",
        command="python publish_daily_sales.py --date {{ macros.ds_add(ds, -1) }} --mode merge "
                "--try-number {{ ti.try_number }} --crash-on-try 1",
        environment=SNOWFLAKE_ENV,
        mounts=KEY_MOUNT,
        mount_tmp_dir=False,
        auto_remove="success",
    )

    ingest_orders >> dbt_build >> publish_daily_sales
