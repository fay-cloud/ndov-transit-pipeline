# Architecture Documentation

## Pipeline Overview

This project implements a batch data pipeline that ingests Dutch public
transport schedule data (GTFS Static) from NDOVloket, stores it in
Azure Data Lake Storage Gen2, transforms it in Snowflake using dbt,
and visualizes it in a dashboard.

## Components

| Component        | Tool                          | Purpose                              |
|------------------|-------------------------------|--------------------------------------|
| Ingestion        | Python + requests             | Download GTFS ZIP from NDOVloket     |
| Data Lake        | Azure Data Lake Storage Gen2  | Store raw and processed data files   |
| Orchestration    | Apache Airflow                | Schedule and monitor pipeline runs   |
| Data Warehouse   | Snowflake                     | Store and query transformed data     |
| Transformation   | dbt                           | Model, test and document data        |
| Streaming Layer  | Apache Kafka + Flink          | Lightweight streaming component      |
| CI/CD            | GitHub Actions                | Lint, test and validate on push      |
| Containerization | Docker                        | Reproducible local environment       |

## Data Flow

NDOVloket --> Python Script --> Azure Data Lake (raw/)
                                      |
                              Airflow triggers
                                      |
                              Snowflake (raw tables)
                                      |
                              dbt models (staging --> marts)
                                      |
                              Dashboard (two tiles)

## Data Lake Folder Structure

ndov-gtfs/
  raw/
    gtfs/
      YYYY/MM/DD/
        gtfs_static.zip