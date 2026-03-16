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

## Setup
Instructions coming as the project progresses.