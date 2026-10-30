"""Run from the repository root in the redgrave-airflow:1.0.0 image."""
import runpy
from airflow import macros

dag = runpy.run_path("airflow/dags/redgrave_daily.py")["dag"]
assert set(dag.task_ids) == {"ingest_orders", "dbt_build", "publish_daily_sales"}
assert dag.get_task("ingest_orders").downstream_task_ids == {"dbt_build"}
assert dag.get_task("dbt_build").downstream_task_ids == {"publish_daily_sales"}
assert dag.max_active_runs == 1
assert str(dag.timezone) == "Europe/London"
for task in dag.tasks:
    assert task.retries == 2
    assert all(mount["ReadOnly"] for mount in task.mounts)
publish = dag.get_task("publish_daily_sales")
class Attempt:
    try_number = 2
command = dag.get_template_env().from_string(publish.command).render(
    ds="2026-08-04", macros=macros, ti=Attempt())
assert "--date 2026-08-03 --mode merge --try-number 2 --crash-on-try 1" in command
print("DAG valid: dependencies, retries, key mount and backfill date checked.")
