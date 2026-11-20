# Storage Architecture

## 1. Overview

Phase 3 implements two complementary storage layers:

- Object storage: PGSTY Silo
- Relational warehouse: PostgreSQL

Silo provides an S3-compatible object storage API. PostgreSQL stores
structured source data in a dedicated raw schema.

The two services run locally using Docker Compose.

## 2. Object Storage

Implementation: PGSTY Silo

Docker image:
`docker.io/pgsty/silo:RELEASE.2026-11-12T00-00-00Z`

Local endpoints:

- S3 API: `http://localhost:9000`
- Web console: `http://localhost:9001`

Bucket:

`olist-raw`

The bucket contains the original Olist ZIP archive and all nine extracted
CSV source files, for a total of ten objects.

The object storage layer preserves source files without modifying them.
SHA-256 checksums were compared between local source files and downloaded
Silo objects; the comparison returned no differences.

Object persistence was also checked after restarting the Silo container.

## 3. Relational Warehouse

Implementation: PostgreSQL 17 (Alpine image)

Database:

`olist_warehouse`

Schemas:

- `public`: PostgreSQL default schema and development validation objects.
- `raw`: source-aligned tables loaded from the Olist CSV datasets.

The raw schema contains nine tables:

- customers
- geolocation
- order_items
- order_payments
- order_reviews
- orders
- products
- sellers
- product_category_name_translation

The raw layer preserves source-level data. Cleaning, business rules,
standardization, and analytical modelling belong in later transformation
layers.

## 4. Data Loading

Python and Pandas are used to read CSV files in chunks.

SQLAlchemy and Psycopg provide PostgreSQL connectivity.

The loader:

1. Maps each source CSV to its corresponding raw table.
2. Reads data in manageable chunks.
3. Applies explicit source-aware data types.
4. Converts numeric and timestamp values for database insertion.
5. Loads each dataset in a transaction.

The loader uses a truncate-and-reload approach for each dataset.
Each dataset is handled in its own transaction.

## 5. Loaded Dataset Volumes

| Dataset | Rows |
|---|---:|
| customers | 99,441 |
| geolocation | 1,000,163 |
| order_items | 112,650 |
| order_payments | 103,886 |
| order_reviews | 99,224 |
| orders | 99,441 |
| products | 32,951 |
| sellers | 3,095 |
| product_category_name_translation | 71 |
| **Total** | **1,550,922** |

## 6. Data Integrity Checks

The following checks were performed after loading:

- Source and target row counts were compared.
- Expected unique keys were checked for duplicate groups.
- Core relationships were checked for orphan records.
- Decimal column precision and scale were inspected.
- Object storage checksums were compared against source files.

No duplicate groups were found for the tested business keys:

- customers.customer_id
- orders.order_id
- products.product_id
- sellers.seller_id
- order_items (order_id, order_item_id)
- order_payments (order_id, payment_sequential)

No orphan records were found in the tested core relationships.

Geolocation is an exception to simple uniqueness assumptions:
the source contains repeated records, so its postal-code prefix must not
be treated as a unique key.

The raw layer intentionally does not impose analytical primary-key or
foreign-key constraints on all source tables.

## 7. Docker Persistence

Docker Compose defines named volumes:

- `postgres_data` mounted at `/var/lib/postgresql/data`
- `silo_data` mounted at `/data`

These volumes preserve database and object-store data independently
of the container lifecycle.

The services bind their ports to localhost rather than exposing them
on all network interfaces.

## 8. Configuration and Secrets

Runtime credentials are stored in the repository-root `.env` file.

The `.env` file is excluded from Git.

`.env.example` documents the required variable names using placeholders.
Actual passwords must never be committed.

Compose commands use the explicit root environment file because the
Compose file is located under the `docker/` directory:

`docker compose --env-file .env -f docker/docker-compose.yml`

## 9. Design Decisions

- Silo is used as the S3-compatible object storage implementation.
- PostgreSQL remains the primary relational warehouse.
- Raw source files are retained separately from structured raw tables.
- Pandas chunk processing is preferred for the current dataset size.
- DuckDB may be evaluated later as an optional analytical engine;
  it does not replace PostgreSQL.
- Distributed processing is deferred until justified by scale or
  learning objectives.
