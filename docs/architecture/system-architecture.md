
# System Architecture

## 1. Architecture Overview

The E-commerce Data Intelligence Platform follows a
modular data engineering architecture.

It consists of data ingestion, object storage, a
relational data warehouse, transformation, orchestration,
business intelligence, and machine learning components.

## 2. Data Sources

Brazilian E-Commerce Public Dataset by Olist.

Primary entities:
- Orders
- Order items
- Customers
- Products
- Sellers
- Payments
- Reviews
- Geolocation
- Product category translations

## 3. Data Ingestion

Technology: Python

Responsibilities:
- Read source datasets.
- Validate file structure.
- Check data quality.
- Load data into raw storage.
- Maintain ingestion metadata.

## 4. Storage

Object Storage: MinIO

Data Warehouse: PostgreSQL

Raw source files will be retained in object storage.
Structured analytical data will be loaded into PostgreSQL.

## 5. Transformation

Technology: dbt

Layers:
- Staging
- Intermediate
- Marts

Transformations will include cleaning, joining, aggregation,
business logic, and data quality tests.

## 6. Orchestration

Technology: Apache Airflow

Responsibilities:
- Coordinate ingestion.
- Trigger transformations.
- Manage task dependencies.
- Monitor pipeline execution.

## 7. Business Intelligence

Technology: Metabase

Dashboards:
- Sales performance
- Product performance
- Customer analytics
- Geographical analytics
- Delivery performance

## 8. Machine Learning

Technologies: Python, Pandas, Scikit-learn, MLflow

Planned models:
- Late delivery prediction
- Customer segmentation
- Customer repurchase-risk analysis
- Product recommendation

## 9. Advanced Extensions

Potential technologies:
- Apache Spark for distributed processing.
- Apache Kafka for event streaming.

These will be evaluated as advanced extensions.

## 10. Development and Version Control

- Docker for service isolation.
- Git for version control.
- GitHub for source code and documentation.
- Automated tests for data and code quality.

## 11. Resource and Deployment Strategy

The project will initially run on a local development
environment using Docker and WSL2.

Because development hardware has limited memory and
disk capacity, services will be started selectively
rather than running the entire stack simultaneously.

Implementation priorities:

1. Build ingestion and storage pipelines first.
2. Introduce PostgreSQL and dbt for transformations.
3. Add Airflow for workflow orchestration.
4. Introduce Metabase for business dashboards.
5. Add machine learning workflows and MLflow.
6. Evaluate Spark and Kafka as optional extensions.

The initial implementation will prioritize lightweight
processing with Python and Pandas.

Distributed processing will be introduced only if
dataset size or learning objectives justify it.
