"""Unit tests for the PostgreSQL raw data loader."""

import unittest
from decimal import Decimal

import pandas as pd

from sqlalchemy import Integer, Numeric

from storage.loader import (
    CSV_TO_TABLE,
    _get_csv_dtypes,
    _get_sql_dtypes,
    _prepare_chunk,
)


class TestRawDataLoader(unittest.TestCase):

    def test_all_nine_datasets_are_configured(self):
        self.assertEqual(len(CSV_TO_TABLE), 9)

    def test_customer_identifiers_and_postal_codes_are_strings(self):
        dtypes = _get_csv_dtypes(
            "olist_customers_dataset.csv"
        )

        self.assertEqual(dtypes["customer_id"], "string")
        self.assertEqual(
            dtypes["customer_zip_code_prefix"],
            "string",
        )

    def test_unsupported_dataset_is_rejected(self):
        with self.assertRaises(ValueError):
            _get_csv_dtypes("unknown.csv")

    def test_order_items_are_prepared_correctly(self):
        chunk = pd.DataFrame({
            "order_id": ["order_1"],
            "order_item_id": pd.array([1], dtype="Int64"),
            "product_id": ["product_1"],
            "seller_id": ["seller_1"],
            "shipping_limit_date": [
                "2017-09-19 09:45:35"
            ],
            "price": ["99.90"],
            "freight_value": ["15.50"],
        })

        prepared = _prepare_chunk(
            "olist_order_items_dataset.csv",
            chunk,
        )

        self.assertEqual(
            prepared.loc[0, "price"],
            Decimal("99.90"),
        )

        self.assertEqual(
            prepared.loc[0, "freight_value"],
            Decimal("15.50"),
        )

        self.assertIsInstance(
            prepared.loc[0, "shipping_limit_date"],
            pd.Timestamp,
        )

    def test_missing_decimal_values_are_preserved(self):
        chunk = pd.DataFrame({
            "order_id": ["order_1"],
            "order_item_id": [1],
            "product_id": ["product_1"],
            "seller_id": ["seller_1"],
            "shipping_limit_date": [
                "2017-09-19 09:45:35"
            ],
            "price": ["99.90"],
            "freight_value": [None],
        })

        prepared = _prepare_chunk(
            "olist_order_items_dataset.csv",
            chunk,
        )

        self.assertIsNone(
            prepared.loc[0, "freight_value"]
        )

    def test_unexpected_columns_are_rejected(self):
        chunk = pd.DataFrame({
            "incorrect_column": [1]
        })

        with self.assertRaises(ValueError):
            _prepare_chunk(
                "olist_customers_dataset.csv",
                chunk,
            )

    def test_order_items_database_types_are_explicit(self):
        sql_dtypes = _get_sql_dtypes(
            "olist_order_items_dataset.csv"
        )

        self.assertIsInstance(
            sql_dtypes["price"],
            Numeric,
        )

        self.assertEqual(sql_dtypes["price"].precision, 12)
        self.assertEqual(sql_dtypes["price"].scale, 2)

        self.assertIsInstance(
            sql_dtypes["order_item_id"],
            Integer,
        )


if __name__ == "__main__":
    unittest.main()
