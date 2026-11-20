"""Load Olist CSV datasets into PostgreSQL raw tables."""

from decimal import Decimal
from pathlib import Path

import pandas as pd
from sqlalchemy import Integer, Numeric, inspect, text
from sqlalchemy.engine import Engine

from ingestion.config import OLIST_RAW_DIR
from ingestion.extract import read_csv_in_chunks
from ingestion.schemas import OLIST_SCHEMAS

from storage.database import get_engine


# Source CSV filename -> PostgreSQL table name.
CSV_TO_TABLE = {
    "olist_customers_dataset.csv": "customers",
    "olist_geolocation_dataset.csv": "geolocation",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_orders_dataset.csv": "orders",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv":
        "product_category_name_translation",
}


# Columns that must remain strings in Pandas.
TEXT_COLUMNS = {
    "customers": [
        "customer_id", "customer_unique_id",
        "customer_zip_code_prefix", "customer_city",
        "customer_state",
    ],
    "geolocation": [
        "geolocation_zip_code_prefix",
        "geolocation_city", "geolocation_state",
    ],
    "order_items": [
        "order_id", "product_id", "seller_id",
    ],
    "order_payments": [
        "order_id", "payment_type",
    ],
    "order_reviews": [
        "review_id", "order_id",
        "review_comment_title", "review_comment_message",
    ],
    "orders": [
        "order_id", "customer_id", "order_status",
    ],
    "products": [
        "product_id", "product_category_name",
    ],
    "sellers": [
        "seller_id", "seller_zip_code_prefix",
        "seller_city", "seller_state",
    ],
    "product_category_name_translation": [
        "product_category_name",
        "product_category_name_english",
    ],
}


# Nullable integer columns.
INTEGER_COLUMNS = {
    "order_items": ["order_item_id"],
    "order_payments": [
        "payment_sequential", "payment_installments",
    ],
    "order_reviews": ["review_score"],
    "products": [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ],
}


# Monetary columns requiring exact decimal representation.
DECIMAL_COLUMNS = {
    "order_items": ["price", "freight_value"],
    "order_payments": ["payment_value"],
}


# Timestamp columns.
DATETIME_COLUMNS = {
    "order_items": ["shipping_limit_date"],
    "order_reviews": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
}


def _get_sql_dtypes(filename: str) -> dict:
    """Return explicit SQLAlchemy types for database insertion."""

    table_name = CSV_TO_TABLE[filename]
    sql_dtypes = {}

    for column in DECIMAL_COLUMNS.get(table_name, []):
        sql_dtypes[column] = Numeric(12, 2)

    for column in INTEGER_COLUMNS.get(table_name, []):
        sql_dtypes[column] = Integer()

    return sql_dtypes


def _get_csv_dtypes(filename: str) -> dict[str, str]:
    """Return explicit Pandas data types for a source dataset."""

    if filename not in CSV_TO_TABLE:
        raise ValueError(f"Unsupported dataset: {filename}")

    table_name = CSV_TO_TABLE[filename]

    dtypes = {
        column: "string"
        for column in TEXT_COLUMNS.get(table_name, [])
    }

    dtypes.update({
        column: "Int64"
        for column in INTEGER_COLUMNS.get(table_name, [])
    })

    # Read decimal and timestamp values as strings first.
    # They are converted explicitly before database insertion.
    dtypes.update({
        column: "string"
        for column in DECIMAL_COLUMNS.get(table_name, [])
    })

    dtypes.update({
        column: "string"
        for column in DATETIME_COLUMNS.get(table_name, [])
    })

    return dtypes


def _to_decimal(value):
    """Convert a value to Decimal without floating-point rounding."""

    if pd.isna(value):
        return None

    return Decimal(str(value))


def _prepare_chunk(
    filename: str,
    chunk: pd.DataFrame,
) -> pd.DataFrame:
    """Validate source columns and prepare values for PostgreSQL."""

    if filename not in CSV_TO_TABLE:
        raise ValueError(f"Unsupported dataset: {filename}")

    expected_columns = OLIST_SCHEMAS[filename]

    if list(chunk.columns) != expected_columns:
        raise ValueError(
            f"Unexpected columns in {filename}. "
            f"Expected: {expected_columns}. "
            f"Received: {list(chunk.columns)}"
        )

    table_name = CSV_TO_TABLE[filename]
    prepared = chunk.copy()

    for column in DATETIME_COLUMNS.get(table_name, []):
        prepared[column] = pd.to_datetime(
            prepared[column],
            errors="raise",
        )

    for column in DECIMAL_COLUMNS.get(table_name, []):
        prepared[column] = prepared[column].map(_to_decimal)

    return prepared


def load_dataset(
    engine: Engine,
    filename: str,
    chunk_size: int = 25_000,
) -> int:
    """Replace one raw table with data from its source CSV.

    The table replacement and all inserts occur in one transaction.
    If loading fails, PostgreSQL rolls back the transaction.
    """

    if filename not in CSV_TO_TABLE:
        raise ValueError(f"Unsupported dataset: {filename}")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    table_name = CSV_TO_TABLE[filename]
    file_path = OLIST_RAW_DIR / filename

    csv_chunks = read_csv_in_chunks(
        file_path,
        chunk_size=chunk_size,
        dtype=_get_csv_dtypes(filename),
    )

    rows_loaded = 0
    chunks_loaded = 0

    with engine.begin() as connection:

        if not inspect(connection).has_table(
            table_name,
            schema="raw",
        ):
            raise RuntimeError(
                f"Target table raw.{table_name} does not exist."
            )

        # Clear the old dataset inside the transaction.
        # A failure later will restore its previous contents.
        connection.execute(
            text(f"TRUNCATE TABLE raw.{table_name}")
        )

        for chunk in csv_chunks:
            prepared = _prepare_chunk(filename, chunk)

            prepared.to_sql(
                name=table_name,
                schema="raw",
                con=connection,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=1_000,
                dtype=_get_sql_dtypes(filename),
            )

            rows_loaded += len(prepared)
            chunks_loaded += 1

        if chunks_loaded == 0:
            raise RuntimeError(
                f"No data rows were found in {filename}."
            )

    return rows_loaded


def load_all_datasets(
    chunk_size: int = 25_000,
) -> dict[str, int]:
    """Load all nine datasets and return their inserted row counts."""

    engine = get_engine()
    results = {}

    try:
        for filename, table_name in CSV_TO_TABLE.items():
            print(f"\nLoading {filename}...")

            rows = load_dataset(
                engine=engine,
                filename=filename,
                chunk_size=chunk_size,
            )

            results[table_name] = rows

            print(
                f"Completed raw.{table_name}: "
                f"{rows:,} rows"
            )

    finally:
        engine.dispose()

    return results
