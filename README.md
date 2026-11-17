# E-commerce Data Intelligence Platform

## Project Overview

An end-to-end data engineering, analytics, and machine learning platform built using the Brazilian E-Commerce Public Dataset by Olist.

The project aims to demonstrate how raw e-commerce data can be ingested, stored, transformed, analyzed, and used to generate business insights through analytics, dashboards, and machine learning.

The platform is being developed incrementally using open-source technologies and tools, with an emphasis on reliability, scalability, data quality, and reproducibility.

## Project Objectives

- Build reliable data ingestion pipelines.
- Store and manage raw and processed datasets.
- Develop scalable data transformation workflows.
- Implement data quality checks and validation.
- Analyze sales, products, customers, payments, and delivery performance.
- Build interactive business intelligence dashboards.
- Apply machine learning and data science techniques to discover patterns and predict business outcomes.
- Develop an end-to-end, production-minded data engineering architecture.

## Dataset

**Brazilian E-Commerce Public Dataset by Olist**

The dataset contains approximately 100,000 orders from Brazilian e-commerce marketplaces, including information about:

- Customers
- Orders
- Order items
- Payments
- Reviews
- Products
- Sellers
- Geolocation
- Product categories

The original source archive and extracted CSV files are stored locally under `data/raw/olist/` and excluded from Git version control.

## Technology Stack

### Currently Used

- Python 3.12
- Pandas
- Git and GitHub
- WSL2 / Ubuntu
- Docker Desktop
- Visual Studio Code

### Planned Technologies

- PostgreSQL – Relational data storage
- MinIO – Object storage
- Apache Airflow – Workflow orchestration
- dbt – Data transformation and modeling
- Apache Spark – Distributed data processing
- Apache Kafka – Event streaming
- Scikit-learn – Machine learning
- Metabase – Business intelligence and dashboards

The technology stack will be introduced progressively as the project evolves.

## Project Architecture

The project follows a modular architecture:

```text
ecommerce-data-intelligence/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── analytics/
│   └── metadata/
│
├── docs/
│   └── ingestion/
│
├── scripts/
│
├── src/
│   ├── ingestion/
│   ├── transformation/
│   ├── analytics/
│   ├── ml/
│   └── storage/
│
├── tests/
│   └── ingestion/
│
├── pyproject.toml
├── .gitignore
└── README.md
```

## Current Project Status

### Phase 1 – Project Foundation and Architecture
Completed.

- Development environment established.
- Git repository initialized and connected to GitHub.
- Project directory structure created.
- Initial architecture and technology choices established.

### Phase 2 – Data Understanding and Ingestion
In progress.

Completed:
- Dataset acquisition and exploration.
- Data profiling and relationship analysis.
- Source schema definitions for all nine CSV datasets.
- Chunk-based CSV ingestion.
- Structural validation.
- Ingestion execution metadata and JSON manifests.
- Error handling and failure reporting.
- Automated ingestion tests (28 tests passing).
- Raw-data storage and Git exclusion strategy.

Remaining:
- Final documentation and project review.

## Running the Ingestion Pipeline

From the project root, activate the virtual environment:

```bash
source .venv/bin/activate
```

Install the project in editable mode if it has not already been installed:

```bash
python -m pip install -e .
```

Run the ingestion pipeline:

```bash
python scripts/run_ingestion.py
```

The pipeline reads the nine registered CSV datasets in chunks, validates their structural schemas, and records ingestion statistics.

Generated run metadata is saved under:

```text
data/metadata/ingestion/
```

## Running Tests

Execute the ingestion test suite:

```bash
python -m unittest discover -s tests/ingestion -v
```

The tests cover extraction, validation, pipeline execution, metadata persistence, and error handling.

## Data Management Principles

- Preserve raw source data without modifying original values.
- Keep raw datasets outside Git version control.
- Validate source structure during ingestion.
- Record ingestion metrics and execution metadata.
- Handle data cleaning, missing values, and business rules in downstream transformation stages.
- Use automated tests to improve pipeline reliability.

## Learning and Development Goals

This project is also a practical learning exercise covering:

- Data engineering fundamentals
- ETL/ELT pipeline design
- Data quality and validation
- Data modeling and warehousing
- Workflow orchestration
- Distributed data processing
- Business intelligence
- Exploratory data analysis
- Machine learning and predictive analytics

The final objective is to build a complete, reproducible, and portfolio-ready data intelligence platform.