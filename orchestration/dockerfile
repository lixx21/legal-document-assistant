# Use the official Airflow image
FROM apache/airflow:2.9.3

USER airflow

ENV AIRFLOW_HOME=/opt/airflow/orchestration
WORKDIR /opt/airflow/orchestration

COPY requirements.txt /opt/airflow/orchestration/requirements.txt
RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt
