# Architecture Documentation

## Problem Statement
Build a dashboard showing Dutch public transport route coverage by operator
and scheduled trip volume by time of day and day of week, using open GTFS
Static data from OVapi (Netherlands combined feed).

## Architecture Overview

### Data Flow
OVapi (gtfs-nl.zip)
    --> Python ingestion script (gtfs_downloader.py)
        --> Azure Data Lake Storage Gen2 (raw/gtfs/YYYY/MM/DD/)
            --> Snowflake raw tables (loaded by Airflow)
                --> dbt staging models (clean and type)
                    --> dbt mart models (aggregate for dashboard)
                        --> Dashboard (two tiles)

Parallel streaming layer:
OVapi --> Kafka topic --> Flink job --> Snowflake (streaming events table)

## Component Decisions

| Component       | Tool                         | Why chosen                                              |
|-----------------|------------------------------|---------------------------------------------------------|
| Ingestion       | Python + requests            | Simple HTTP download, no special client needed          |
| Data Lake       | Azure Data Lake Storage Gen2 | Industry standard, integrates with Snowflake            |
| Orchestration   | Apache Airflow               | Industry standard batch scheduler, DAG-based            |
| Data Warehouse  | Snowflake                    | Native dbt support, widely used in Netherlands          |
| Transformation  | dbt (Snowflake adapter)      | SQL-based, testable, version controlled models          |
| Streaming       | Kafka + Flink                | Demonstrates streaming concepts alongside batch         |
| CI/CD           | GitHub Actions               | Native GitHub integration, free for public repos        |
| Containers      | Docker                       | Reproducible local and CI environment                   |

## Data Lake Structure
```
ndov-gtfs/
  raw/
    gtfs/
      YYYY/
        MM/
          DD/
            gtfs_static.zip
```

## Snowflake Structure
```
NDOV_DB/
  RAW/
    raw_agency
    raw_routes
    raw_stops
    raw_trips
    raw_stop_times
    raw_calendar_dates
  STAGING/
    stg_agency
    stg_routes
    stg_stops
    stg_trips
    stg_stop_times
  MARTS/
    mart_route_coverage
    mart_trip_volume_by_hour
```

## Dashboard Tiles

Tile 1: Route coverage by operator
  Source table: mart_route_coverage
  Shows: number of routes per operator across the Netherlands

Tile 2: Trip volume by time of day and day of week
  Source table: mart_trip_volume_by_hour
  Shows: when the Dutch public transport network is busiest

## Batch Pipeline Schedule
The pipeline runs once daily at 06:00 UTC, after OVapi publishes
the latest timetable update.

## CI/CD
Every push to main or a pull request triggers GitHub Actions which:
  - Lints Python files with flake8
  - Checks Python syntax
  - Future: runs dbt model compilation check