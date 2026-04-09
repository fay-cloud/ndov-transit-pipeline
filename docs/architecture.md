# Architecture Documentation

## Problem Statement
Build a dashboard showing Dutch public transport route coverage by operator
and scheduled trip volume by time of day and day of week, using open GTFS
Static data from OVapi, the Netherlands combined public transport feed.

## Architecture Overview

### Data Flow

OVapi (gtfs-nl.zip)
--> Python ingestion script (gtfs_downloader.py)
--> Azure Data Lake Storage Gen2 (raw/gtfs/2026/03/30/)
--> Snowflake RAW tables (loaded by Airflow)
--> dbt staging models (clean and type)
--> dbt mart models (aggregate for dashboard)
--> Power BI Dashboard 

## Component Decisions

| Component      | Tool                         | Why chosen                                           |
|----------------|------------------------------|------------------------------------------------------|
| Ingestion      | Python + requests            | Simple HTTP download, no special client needed       |
| Data Lake      | Azure Data Lake Storage Gen2 | Industry standard object storage for raw data        |
| Orchestration  | Apache Airflow               | Industry standard batch scheduler, DAG-based         |
| Data Warehouse | Snowflake                    | Native dbt support, widely used in Netherlands       |
| Transformation | dbt (Snowflake adapter)      | SQL-based, testable, version controlled models       |
| Dashboard      | Power BI                     | Widely used in Dutch organisations, known by team    |
| CI/CD          | GitHub Actions               | Native GitHub integration, free for public repos     |
| Containers     | Docker                       | Reproducible local and CI environment                |

## Pipeline Type
Batch pipeline running once daily at 06:00 UTC after OVapi publishes
the latest timetable update. The pipeline checks if today's data already
exists in Azure before downloading to avoid rate limiting.

## Data Lake Structure
datalakesproj1/
ndov-gtfs/
raw/
gtfs/
2026/
03/
30/
agency.parquet
routes.parquet
stops.parquet
trips.parquet
stop_times.parquet
calendar_dates.parquet
feed_info.parquet

## Snowflake Structure
NDOV_DB/
RAW/
raw_agency
raw_routes
raw_stops
raw_trips
raw_stop_times
raw_calendar_dates
raw_feed_info
STAGING/
stg_agency
stg_routes
stg_stops
stg_trips
stg_stop_times
stg_calendar_dates
MARTS/
mart_route_coverage
mart_trip_volume_by_hour

## dbt Model Layers

### Staging Models
Staging models clean and type the raw data. All columns are cast from
VARCHAR to their correct data types. Bad rows are filtered out.
Staging models are materialised as views in Snowflake.

### Mart Models
Mart models aggregate the staged data into dashboard-ready tables.
Mart models are materialised as tables in Snowflake for fast querying.

| Mart Table                  | Powers                              |
|-----------------------------|-------------------------------------|
| mart_route_coverage         | Dashboard Tile 1: Routes by operator|
| mart_trip_volume_by_hour    | Dashboard Tile 2: Trip volume heatmap|

## Dashboard

Tool: Power BI Desktop

### Tile 1: Route Coverage by Operator
- Visual: Clustered bar chart
- Source: mart_route_coverage
- Shows: Number of routes per operator filterable by route type
- Slicer: Bus, Train, Tram, Ferry

### Tile 2: Trip Volume by Hour and Day of Week
- Visual: Matrix heatmap
- Source: mart_trip_volume_by_hour
- Shows: When the Dutch public transport network is busiest

### KPI Cards
- Total Routes Nationwide
- Total Operators
- Total Train Routes
- Total Bus Routes
- Peak Hour

## Airflow DAG
The DAG gtfs_ingestion runs three tasks in sequence:

download_and_upload_gtfs >> load_parquet_to_snowflake >> run_dbt_models

Task 1: Downloads GTFS ZIP from OVapi, converts to Parquet, uploads to Azure.
Skips download if today's files already exist in Azure.

Task 2: Truncates and reloads all raw Snowflake tables from Azure stage.

Task 3: Runs all dbt models to refresh staging views and mart tables.

## CI/CD
Every push to main or a pull request triggers GitHub Actions which:
- Lints Python files with flake8
- Checks Python syntax on ingestion scripts
- Future: runs dbt model compilation check

## Data Source
OVapi GTFS NL combined feed covering all Dutch public transport operators
including NS, GVB, RET, HTM, Arriva, Connexxion, Qbuzz and 35 others.
Feed URL: https://gtfs.ovapi.nl/nl/gtfs-nl.zip
Feed validity: Updated daily, covers full annual timetable period.