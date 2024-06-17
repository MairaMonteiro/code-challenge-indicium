from datetime import datetime
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.task_group import TaskGroup
from airflow import DAG

default_args = {}

def meltano_task(task_id, pipeline_name):
    return DockerOperator(
        task_id=task_id,
        image='meltano:1.0',
        container_name='task__pipeline',
        api_version='auto',
        docker_url="unix://var/run/docker.sock",
        auto_remove=True,
        network_mode='bridge',
        entrypoint=[
            "bash",
            "-c",
            f"meltano run {pipeline_name}"
        ]
    )

with DAG(dag_id="indicium_challenge", 
         default_args=default_args, 
         start_date=datetime(2020, 1, 1), 
         schedule_interval="@daily", 
         catchup=False) as dag:

    with TaskGroup(group_id="extracts") as extract_tasks:
        extract_csv = meltano_task('csv', 'extract-csv')
        extract_postgres = meltano_task('postgres', 'extract-postgres')
        send_to_db = meltano_task('northwind', 'send-to-northwind')

    extract_csv >> extract_postgres >> send_to_db
