# NDOV Dutch Public Transport Pipeline

## Project Overview
An end-to-end batch data pipeline built on GTFS Static data from NDOVloket,
the Dutch national public transport data portal.

## Problem Statement
Build a dashboard showing Dutch public transport route coverage by operator
and scheduled trip volume by time of day, using open GTFS data.

## Architecture
See docs/architecture.md

## Stack
- Ingestion: Python + NDOVloket GTFS Static
- Orchestration: Apache Airflow
- Data Lake: Azure Data Lake Storage Gen2
- Data Warehouse: Snowflake
- Transformation: dbt
- Streaming Layer: Apache Kafka + Apache Flink
- CI/CD: GitHub Actions
- Containerization: Docker
## Dashboard Tiles

Tile 1: Route coverage by operator
  Source table: mart_route_coverage
  Tool: Power BI
  Chart type: Map or bar chart showing routes per operator

Tile 2: Trip volume by time of day and day of week
  Source table: mart_trip_volume_by_hour
  Tool: Power BI
  Chart type: Heatmap showing busiest hours across the week
## Setup
Instructions coming as the project progresses.