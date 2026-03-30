FROM apache/airflow:2.8.1-python3.11

USER root

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && apt-get clean

USER airflow

COPY --chown=airflow:root requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt