from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys

sys.path.insert(0, "/opt/airflow/ingestion")
sys.path.insert(0, "/opt/airflow/dags")

from gtfs_downloader import run as run_ingestion
from snowflake_load import load_parquet_to_snowflake


def run_snowflake_load():
    date_partition = datetime.utcnow().strftime("%Y/%m/%d")
    load_parquet_to_snowflake(date_partition)


default_args = {
    "owner": "ndov-pipeline",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="gtfs_ingestion",
    description="Download GTFS Static data from OVapi, store as Parquet in Azure and load into Snowflake",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval="0 6 * * *",
    catchup=False,
    tags=["gtfs", "ingestion", "azure", "snowflake"],
) as dag:

    ingest_gtfs = PythonOperator(
        task_id="download_and_upload_gtfs",
        python_callable=run_ingestion,
    )

    load_to_snowflake = PythonOperator(
        task_id="load_parquet_to_snowflake",
        python_callable=run_snowflake_load,
    )

    ingest_gtfs >> load_to_snowflake