import os
import requests
import logging
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


def download_gtfs_zip() -> bytes:
    """Download the GTFS static ZIP file from NDOVloket."""
    logger.info(f"Downloading GTFS data from {GTFS_URL}")
    response = requests.get(GTFS_URL, timeout=120)
    response.raise_for_status()
    logger.info(f"Download complete. Size: {len(response.content) / 1024:.1f} KB")
    return response.content


def upload_to_azure(data: bytes, blob_name: str) -> None:
    """Upload raw bytes to Azure Data Lake Storage Gen2."""
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={AZURE_STORAGE_ACCOUNT_NAME};"
        f"AccountKey={AZURE_STORAGE_ACCOUNT_KEY};"
        f"EndpointSuffix=core.windows.net"
    )
    client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = client.get_blob_client(
        container=AZURE_CONTAINER_NAME,
        blob=blob_name
    )
    blob_client.upload_blob(data, overwrite=True)
    logger.info(f"Uploaded to Azure: {AZURE_CONTAINER_NAME}/{blob_name}")


def run():
    """Main entry point called by Airflow."""
    date_partition = datetime.utcnow().strftime("%Y/%m/%d")
    blob_name = f"raw/gtfs/{date_partition}/gtfs_static.zip"

    data = download_gtfs_zip()
    upload_to_azure(data, blob_name)
    logger.info("GTFS ingestion complete.")


if __name__ == "__main__":
    run()