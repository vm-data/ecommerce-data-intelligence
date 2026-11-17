from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw" / "olist"


def investigate_orphans(
    child_file,
    child_column,
    parent_file,
    parent_column,
):
    """Display child values that do not exist in the parent dataset."""

    child_df = pd.read_csv(
        DATA_DIRECTORY / child_file,
        usecols=[child_column],
    )

    parent_df = pd.read_csv(
        DATA_DIRECTORY / parent_file,
        usecols=[parent_column],
    )

    parent_values = set(parent_df[parent_column].dropna())

    orphan_values = child_df.loc[
        child_df[child_column].notna()
        & ~child_df[child_column].isin(parent_values),
        child_column,
    ]

    print("\n" + "=" * 65)
    print(f"CHILD DATASET: {child_file}")
    print(f"COLUMN: {child_column}")
    print("=" * 65)

    if orphan_values.empty:
        print("No unmatched values.")
    else:
        print("Unmatched values and their frequencies:")
        print(orphan_values.value_counts().to_string())


def main():
    investigate_orphans(
        "olist_products_dataset.csv",
        "product_category_name",
        "product_category_name_translation.csv",
        "product_category_name",
    )

    investigate_orphans(
        "olist_customers_dataset.csv",
        "customer_zip_code_prefix",
        "olist_geolocation_dataset.csv",
        "geolocation_zip_code_prefix",
    )

    investigate_orphans(
        "olist_sellers_dataset.csv",
        "seller_zip_code_prefix",
        "olist_geolocation_dataset.csv",
        "geolocation_zip_code_prefix",
    )


if __name__ == "__main__":
    main()