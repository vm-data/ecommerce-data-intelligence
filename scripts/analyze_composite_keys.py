from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw" / "olist"


def analyze_composite_key(dataset_name, key_columns):
    """Check whether a combination of columns uniquely identifies rows."""

    dataset_path = DATA_DIRECTORY / dataset_name

    df = pd.read_csv(dataset_path, usecols=key_columns)

    duplicate_count = df.duplicated(subset=key_columns).sum()

    print(f"\nDataset: {dataset_name}")
    print(f"Candidate key: {key_columns}")
    print(f"Total rows: {len(df):,}")
    print(f"Duplicate key combinations: {duplicate_count:,}")

    if duplicate_count == 0:
        print("Result: Candidate composite key is unique.")
    else:
        print("Result: Candidate composite key is NOT unique.")


def investigate_reviews():
    """Investigate repeated review IDs and order IDs."""

    dataset_path = DATA_DIRECTORY / "olist_order_reviews_dataset.csv"

    df = pd.read_csv(
        dataset_path,
        usecols=["review_id", "order_id"],
    )

    print("\nREVIEW RELATIONSHIP INVESTIGATION")
    print("=" * 65)

    # How many orders are associated with each review ID?
    orders_per_review = df.groupby("review_id")["order_id"].nunique()

    print("\nReview IDs associated with multiple orders:")
    print((orders_per_review > 1).sum())

    # How many review IDs are associated with each order?
    reviews_per_order = df.groupby("order_id")["review_id"].nunique()

    print("\nOrders associated with multiple review IDs:")
    print((reviews_per_order > 1).sum())


def main():
    analyze_composite_key(
        "olist_order_items_dataset.csv",
        ["order_id", "order_item_id"],
    )

    analyze_composite_key(
        "olist_order_payments_dataset.csv",
        ["order_id", "payment_sequential"],
    )

    analyze_composite_key(
        "olist_order_reviews_dataset.csv",
        ["review_id", "order_id"],
    )

    investigate_reviews()


if __name__ == "__main__":
    main()