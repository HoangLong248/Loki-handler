"""Example DAG demonstrating the usage of the BashOperator."""
from __future__ import annotations

import datetime

import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="example_bash_operator",
    schedule="0 0 * * *",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    tags=["example", "example2"],
) as dag:
    # [START howto_operator_bash_skip]
    hello_world = BashOperator(
        task_id="hello_world",
        bash_command='echo "hello world hello worldhello worldhello worldhello worldhello worldhello worldhello world"',
)

if __name__ == "__main__":
    dag.test()