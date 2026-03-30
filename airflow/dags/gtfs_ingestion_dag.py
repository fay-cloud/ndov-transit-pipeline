from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys

sys.path.insert(0, "/opt/airflow/ingestion")
from gtfs_downloader import run as run_ingestion

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
    description="Download GTFS Static data from OVapi and store as Parquet in Azure Data Lake",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval="0 6 * * *",
    catchup=False,
    tags=["gtfs", "ingestion", "azure"],
) as dag:

    ingest_gtfs = PythonOperator(
        task_id="download_and_upload_gtfs",
        python_callable=run_ingestion,
    )

    ingest_gtfs