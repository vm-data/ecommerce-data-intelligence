from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw" / "olist"


RELATIONSHIPS = [
    {
        "child": "olist_orders_dataset.csv",
        "child_column": "customer_id",
        "parent": "olist_customers_dataset.csv",
        "parent_column": "customer_id",
    },
    {
        "child": "olist_order_items_dataset.csv",
        "child_column": "order_id",
        "parent": "olist_orders_dataset.csv",
        "parent_column": "order_id",
    },
    {
        "child": "olist_order_items_dataset.csv",
        "child_column": "product_id",
        "parent": "olist_products_dataset.csv",
        "parent_column": "product_id",
    },
    {
        "child": "olist_order_items_dataset.csv",
        "child_column": "seller_id",
        "parent": "olist_sellers_dataset.csv",
        "parent_column": "seller_id",
    },
    {
        "child": "olist_order_payments_dataset.csv",
        "child_column": "order_id",
        "parent": "olist_orders_dataset.csv",
        "parent_column": "order_id",
    },
    {
        "child": "olist_order_reviews_dataset.csv",
        "child_column": "order_id",
        "parent": "olist_orders_dataset.csv",
        "parent_column": "order_id",
    },
    {
        "child": "olist_products_dataset.csv",
        "child_column": "product_category_name",
        "parent": "product_category_name_translation.csv",
        "parent_column": "product_category_name",
    },
    {
        "child": "olist_customers_dataset.csv",
        "child_column": "customer_zip_code_prefix",
        "parent": "olist_geolocation_dataset.csv",
        "parent_column": "geolocation_zip_code_prefix",
    },
    {
        "child": "olist_sellers_dataset.csv",
        "child_column": "seller_zip_code_prefix",
        "parent": "olist_geolocation_dataset.csv",
        "parent_column": "geolocation_zip_code_prefix",
    },
]


def validate_relationship(relationship):
    """Check whether child values exist in the parent dataset."""

    child_path = DATA_DIRECTORY / relationship["child"]
    parent_path = DATA_DIRECTORY / relationship["parent"]

    child_column = relationship["child_column"]
    parent_column = relationship["parent_column"]

    child_df = pd.read_csv(child_path, usecols=[child_column])
    parent_df = pd.read_csv(parent_path, usecols=[parent_column])

    child_values = child_df[child_column].dropna()
    parent_values = set(parent_df[parent_column].dropna())

    missing_count = child_df[child_column].isna().sum()
    orphan_mask = ~child_values.isin(parent_values)

    orphan_rows = orphan_mask.sum()
    orphan_values = child_values[orphan_mask].nunique()

    print("\n" + "=" * 65)
    print(f"{relationship['child']} -> {relationship['parent']}")
    print(f"Relationship: {child_column} -> {parent_column}")
    print("=" * 65)

    print(f"Child rows: {len(child_df):,}")
    print(f"Missing child values: {missing_count:,}")
    print(f"Orphan rows: {orphan_rows:,}")
    print(f"Distinct orphan values: {orphan_values:,}")

    if orphan_rows == 0:
        print("Result: All non-null child values have a parent.")
    else:
        print("Result: Some child values have no matching parent.")


def main():
    for relationship in RELATIONSHIPS:
        validate_relationship(relationship)


if __name__ == "__main__":
    main()