from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw" / "olist"

KEY_CANDIDATES = {
    "olist_customers_dataset.csv": [
        "customer_id",
        "customer_unique_id",
    ],
    "olist_orders_dataset.csv": [
        "order_id",
        "customer_id",
    ],
    "olist_order_items_dataset.csv": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
    ],
    "olist_order_payments_dataset.csv": [
        "order_id",
        "payment_sequential",
    ],
    "olist_order_reviews_dataset.csv": [
        "review_id",
        "order_id",
    ],
    "olist_products_dataset.csv": [
        "product_id",
    ],
    "olist_sellers_dataset.csv": [
        "seller_id",
    ],
    "olist_geolocation_dataset.csv": [
        "geolocation_zip_code_prefix",
    ],
    "product_category_name_translation.csv": [
        "product_category_name",
    ],
}


def analyze_keys(dataset_name, columns):
    """Analyze uniqueness of candidate key columns."""

    dataset_path = DATA_DIRECTORY / dataset_name
    df = pd.read_csv(dataset_path, usecols=columns)

    print("\n" + "=" * 65)
    print(f"DATASET: {dataset_name}")
    print("=" * 65)

    for column in columns:
        total = len(df)
        unique = df[column].nunique()
        duplicates = df[column].duplicated().sum()
        nulls = df[column].isna().sum()

        print(f"\nColumn: {column}")
        print(f"Total records: {total:,}")
        print(f"Unique values: {unique:,}")
        print(f"Duplicate values: {duplicates:,}")
        print(f"Missing values: {nulls:,}")


def main():
    for dataset_name, columns in KEY_CANDIDATES.items():
        analyze_keys(dataset_name, columns)


if __name__ == "__main__":
    main()
