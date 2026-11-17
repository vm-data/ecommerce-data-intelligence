
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ORDERS_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "olist"
    / "olist_orders_dataset.csv"
)


def main():
    """Analyze missing order timestamps by order status."""

    orders = pd.read_csv(ORDERS_PATH)

    timestamp_columns = [
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
    ]

    print("\nORDER STATUS DISTRIBUTION")
    print("=" * 60)

    print(orders["order_status"].value_counts().to_string())

    print("\nMISSING TIMESTAMPS BY ORDER STATUS")
    print("=" * 60)

    summary = orders.groupby("order_status").agg(
        total_orders=("order_id", "size"),
        approval_missing=(
            "order_approved_at",
            lambda column: column.isna().sum(),
        ),
        carrier_missing=(
            "order_delivered_carrier_date",
            lambda column: column.isna().sum(),
        ),
        customer_delivery_missing=(
            "order_delivered_customer_date",
            lambda column: column.isna().sum(),
        ),
    )

    print(summary.to_string())


    # Investigate delivered orders with missing delivery timestamps
    print("\nDELIVERED ORDERS WITH MISSING CUSTOMER DELIVERY DATE")
    print("=" * 60)

    exceptions = orders[
        (orders["order_status"] == "delivered")
        & (orders["order_delivered_customer_date"].isna())
    ]

    print(f"Exception count: {len(exceptions)}")

    print(
        exceptions[
            [
                "order_id",
                "customer_id",
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            ]
        ].to_string(index=False)
    )



if __name__ == "__main__":
    main()
