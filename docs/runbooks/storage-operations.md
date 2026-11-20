# Storage Operations Runbook

## 1. Purpose

This runbook documents routine operations for the local storage
infrastructure used by the E-commerce Data Intelligence Platform.

The storage stack consists of:

- PostgreSQL: relational data warehouse.
- PGSTY Silo: S3-compatible object storage.
- Docker Compose: local service management.

## 2. Prerequisites

- Docker Desktop is running.
- The project virtual environment is available when running Python scripts.
- The root `.env` file exists and contains the local credentials.

Never commit `.env` or share its passwords.

## 3. Docker Compose Command Convention

Run Compose commands from the project root:

    docker compose --env-file .env -f docker/docker-compose.yml

The explicit `--env-file .env` is required because the Compose file
is inside the `docker/` directory while the environment file is
in the project root.

## 4. Start Storage Services

    docker compose --env-file .env -f docker/docker-compose.yml up -d

This starts PostgreSQL and Silo in the background.

Check service status:

    docker compose --env-file .env -f docker/docker-compose.yml ps

Both services should report healthy status.

## 5. Verify PostgreSQL

Check whether PostgreSQL accepts connections:

    docker compose --env-file .env -f docker/docker-compose.yml exec postgres pg_isready -U olist_admin -d olist_warehouse

Open the PostgreSQL shell:

    docker compose --env-file .env -f docker/docker-compose.yml exec postgres psql -U olist_admin -d olist_warehouse

Inspect schemas:

    \dn

Inspect raw tables:

    \dt raw.*

Check row counts:

    SELECT 'customers' AS dataset, COUNT(*) FROM raw.customers
    UNION ALL SELECT 'geolocation', COUNT(*) FROM raw.geolocation
    UNION ALL SELECT 'order_items', COUNT(*) FROM raw.order_items
    UNION ALL SELECT 'order_payments', COUNT(*) FROM raw.order_payments
    UNION ALL SELECT 'order_reviews', COUNT(*) FROM raw.order_reviews
    UNION ALL SELECT 'orders', COUNT(*) FROM raw.orders
    UNION ALL SELECT 'products', COUNT(*) FROM raw.products
    UNION ALL SELECT 'sellers', COUNT(*) FROM raw.sellers
    UNION ALL SELECT 'product_category_name_translation',
                     COUNT(*) FROM raw.product_category_name_translation
    ORDER BY dataset;

Exit the PostgreSQL shell:

    \q

## 6. Verify Silo Object Storage

Configure the Silo client alias inside the container:

    docker compose --env-file .env -f docker/docker-compose.yml exec silo sh -c 'mcli alias set local http://127.0.0.1:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"'

List buckets:

    docker compose --env-file .env -f docker/docker-compose.yml exec silo mcli ls local/

List raw dataset objects:

    docker compose --env-file .env -f docker/docker-compose.yml exec silo mcli ls --recursive local/olist-raw/

Check bucket usage:

    docker compose --env-file .env -f docker/docker-compose.yml exec silo mcli du local/olist-raw/

The expected raw bucket is `olist-raw`.

## 7. Stop Storage Services

Stop the services without deleting their data:

    docker compose --env-file .env -f docker/docker-compose.yml stop

Start them again using the command in Section 4.

## 8. Persistent Storage

Docker Compose manages two named volumes:

- `docker_postgres_data`: PostgreSQL database files.
- `docker_silo_data`: Silo object storage files.

These volumes preserve data when containers are stopped, restarted,
or recreated.

Inspect the volumes:

    docker volume inspect docker_postgres_data docker_silo_data

**Warning:** Do not run `docker compose down -v` unless you deliberately
intend to delete the persistent volumes and their stored data.

## 9. Troubleshooting

### Docker connection error

Start Docker Desktop and wait for its engine to become ready.
Then verify:

    docker info

### PostgreSQL is not healthy

Inspect PostgreSQL logs:

    docker compose --env-file .env -f docker/docker-compose.yml logs postgres

### Silo is not healthy

Inspect Silo logs:

    docker compose --env-file .env -f docker/docker-compose.yml logs silo

### Services are stopped

Check their status and start them again:

    docker compose --env-file .env -f docker/docker-compose.yml ps

    docker compose --env-file .env -f docker/docker-compose.yml up -d

## 10. Data Loading

The raw PostgreSQL tables are populated by:

    python scripts/load_raw_data.py

The loader reads the source CSV files in chunks and loads them into
the corresponding tables in the `raw` schema.

Each dataset is loaded within its own database transaction.
