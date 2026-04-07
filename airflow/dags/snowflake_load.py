import os
import snowflake.connector
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")

TABLES = [
    "raw_agency",
    "raw_routes",
    "raw_stops",
    "raw_trips",
    "raw_stop_times",
    "raw_calendar_dates",
    "raw_feed_info",
]

PARQUET_FILES = {
    "raw_agency": "agency.parquet",
    "raw_routes": "routes.parquet",
    "raw_stops": "stops.parquet",
    "raw_trips": "trips.parquet",
    "raw_stop_times": "stop_times.parquet",
    "raw_calendar_dates": "calendar_dates.parquet",
    "raw_feed_info": "feed_info.parquet",
}


def load_parquet_to_snowflake(date_partition: str) -> None:
    """Load Parquet files from Azure stage into Snowflake raw tables."""
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        database=SNOWFLAKE_DATABASE,
        warehouse=SNOWFLAKE_WAREHOUSE,
        role=SNOWFLAKE_ROLE,
        schema="RAW"
    )
    cursor = conn.cursor()
    try:
        for table, parquet_file in PARQUET_FILES.items():
            stage_path = (
                f"@NDOV_DB.RAW.azure_gtfs_stage"
                f"/raw/gtfs/{date_partition}/{parquet_file}"
            )
            truncate_sql = f"TRUNCATE TABLE NDOV_DB.RAW.{table};"
            copy_sql = f"""
                COPY INTO NDOV_DB.RAW.{table}
                FROM {stage_path}
                FILE_FORMAT = (TYPE = PARQUET)
                MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
            """
            logger.info(f"Truncating {table}")
            cursor.execute(truncate_sql)
            logger.info(f"Loading {parquet_file} into {table}")
            cursor.execute(copy_sql)
            result = cursor.fetchone()
            logger.info(f"{table}: {result}")
    finally:
        cursor.close()
        conn.close()
        logger.info("Snowflake connection closed.")