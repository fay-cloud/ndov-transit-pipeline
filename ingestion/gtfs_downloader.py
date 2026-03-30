import os
import io
import zipfile
import logging
import requests
import pandas as pd
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GTFS_URL = os.getenv("NDOV_GTFS_URL")
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

# These are the GTFS files we want to extract and store
GTFS_FILES = [
    "agency.txt",
    "routes.txt",
    "stops.txt",
    "trips.txt",
    "stop_times.txt",
    "calendar_dates.txt",
    "feed_info.txt",
]


def download_gtfs_zip() -> bytes:
    """Download the GTFS static ZIP file from OVapi."""
    logger.info(f"Downloading GTFS data from {GTFS_URL}")
    response = requests.get(GTFS_URL, timeout=120)
    response.raise_for_status()
    logger.info(f"Download complete. Size: {len(response.content) / 1024 / 1024:.1f} MB")
    return response.content


def extract_and_convert_to_parquet(zip_bytes: bytes) -> dict:
    """Extract GTFS txt files from ZIP and convert each to Parquet format."""
    parquet_files = {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        available_files = zf.namelist()
        logger.info(f"Files found in ZIP: {available_files}")
        for gtfs_file in GTFS_FILES:
            if gtfs_file not in available_files:
                logger.warning(f"{gtfs_file} not found in ZIP, skipping.")
                continue
            with zf.open(gtfs_file) as f:
                df = pd.read_csv(f, dtype=str)
                logger.info(f"Read {gtfs_file}: {len(df)} rows, {len(df.columns)} columns")
                parquet_buffer = io.BytesIO()
                df.to_parquet(parquet_buffer, index=False, engine="pyarrow")
                parquet_buffer.seek(0)
                parquet_name = gtfs_file.replace(".txt", ".parquet")
                parquet_files[parquet_name] = parquet_buffer.read()
                logger.info(f"Converted {gtfs_file} to {parquet_name}")
    return parquet_files


def upload_to_azure(parquet_files: dict, date_partition: str) -> None:
    """Upload Parquet files to Azure Data Lake Storage Gen2."""
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={AZURE_STORAGE_ACCOUNT_NAME};"
        f"AccountKey={AZURE_STORAGE_ACCOUNT_KEY};"
        f"EndpointSuffix=core.windows.net"
    )
    client = BlobServiceClient.from_connection_string(connection_string)
    for filename, data in parquet_files.items():
        blob_name = f"raw/gtfs/{date_partition}/{filename}"
        blob_client = client.get_blob_client(
            container=AZURE_CONTAINER_NAME,
            blob=blob_name
        )
        blob_client.upload_blob(data, overwrite=True)
        logger.info(f"Uploaded: {AZURE_CONTAINER_NAME}/{blob_name}")


def run():
    """Main entry point called by Airflow."""
    date_partition = datetime.utcnow().strftime("%Y/%m/%d")
    logger.info(f"Starting GTFS ingestion for partition: {date_partition}")
    zip_bytes = download_gtfs_zip()
    parquet_files = extract_and_convert_to_parquet(zip_bytes)
    upload_to_azure(parquet_files, date_partition)
    logger.info(f"Ingestion complete. {len(parquet_files)} Parquet files uploaded.")


if __name__ == "__main__":
    run()