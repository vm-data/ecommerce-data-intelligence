
"""Unit tests for the ingestion pipeline."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from ingestion.pipeline import IngestionError, run_ingestion
from ingestion.schemas import OLIST_SCHEMAS


class TestRunIngestion(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)

        # Create small CSV files matching the registered schemas.
        self.customer_data = pd.DataFrame(
            {
                "customer_id": ["C001"],
                "customer_unique_id": ["U001"],
                "customer_zip_code_prefix": ["01001"],
                "customer_city": ["Sao Paulo"],
                "customer_state": ["SP"],
            }
        )

        self.customer_file = (
            self.data_dir / "olist_customers_dataset.csv"
        )

        self.customer_data.to_csv(
            self.customer_file,
            index=False,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_fails_when_expected_dataset_is_missing(self):
        with self.assertRaisesRegex(
            FileNotFoundError,
            "Missing expected datasets",
        ):
            run_ingestion(self.data_dir)

    def test_fails_when_unregistered_dataset_exists(self):
        for file_name in (
            "olist_geolocation_dataset.csv",
            "olist_order_items_dataset.csv",
            "olist_order_payments_dataset.csv",
            "olist_order_reviews_dataset.csv",
            "olist_orders_dataset.csv",
            "olist_products_dataset.csv",
            "olist_sellers_dataset.csv",
            "product_category_name_translation.csv",
        ):
            (self.data_dir / file_name).touch()

        unexpected_file = self.data_dir / "unexpected.csv"
        unexpected_file.touch()

        with self.assertRaisesRegex(
            ValueError,
            "Unregistered datasets found",
        ):
            run_ingestion(self.data_dir)

    def test_fails_when_dataset_is_empty(self):
        for file_name, columns in {
            "olist_geolocation_dataset.csv": [
                "geolocation_zip_code_prefix",
                "geolocation_lat",
                "geolocation_lng",
                "geolocation_city",
                "geolocation_state",
            ],
            "olist_order_items_dataset.csv": [
                "order_id",
                "order_item_id",
                "product_id",
                "seller_id",
                "shipping_limit_date",
                "price",
                "freight_value",
            ],
            "olist_order_payments_dataset.csv": [
                "order_id",
                "payment_sequential",
                "payment_type",
                "payment_installments",
                "payment_value",
            ],
            "olist_order_reviews_dataset.csv": [
                "review_id",
                "order_id",
                "review_score",
                "review_comment_title",
                "review_comment_message",
                "review_creation_date",
                "review_answer_timestamp",
            ],
            "olist_orders_dataset.csv": [
                "order_id",
                "customer_id",
                "order_status",
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            ],
            "olist_products_dataset.csv": [
                "product_id",
                "product_category_name",
                "product_name_lenght",
                "product_description_lenght",
                "product_photos_qty",
                "product_weight_g",
                "product_length_cm",
                "product_height_cm",
                "product_width_cm",
            ],
            "olist_sellers_dataset.csv": [
                "seller_id",
                "seller_zip_code_prefix",
                "seller_city",
                "seller_state",
            ],
            "product_category_name_translation.csv": [
                "product_category_name",
                "product_category_name_english",
            ],
        }.items():
            pd.DataFrame(columns=columns).to_csv(
                self.data_dir / file_name,
                index=False,
            )

        empty_customer_data = self.customer_data.iloc[0:0]
        empty_customer_data.to_csv(
            self.customer_file,
            index=False,
        )

        with self.assertRaises(IngestionError) as context:
            run_ingestion(self.data_dir)

        error = context.exception
        summary = error.ingestion_summary

        failed_dataset = summary["olist_customers_dataset.csv"]

        self.assertEqual(failed_dataset["status"], "failed")
        self.assertEqual(failed_dataset["rows"], 0)
        self.assertEqual(failed_dataset["chunks"], 0)
        self.assertEqual(failed_dataset["error_type"], "ValueError")
        self.assertIn(
            "Dataset is empty",
            failed_dataset["error_message"],
        )

    def test_preserves_partial_summary_when_dataset_fails(self):
        for file_name, columns in OLIST_SCHEMAS.items():
            if file_name == "olist_customers_dataset.csv":
                continue

            if file_name == "olist_geolocation_dataset.csv":
                # Intentionally create an invalid schema.
                pd.DataFrame(
                    {"wrong_column": ["sample"]}
                ).to_csv(
                    self.data_dir / file_name,
                    index=False,
                )
            else:
                pd.DataFrame(
                    [dict.fromkeys(columns, "sample")]
                ).to_csv(
                    self.data_dir / file_name,
                    index=False,
                )

        with self.assertRaises(IngestionError) as context:
            run_ingestion(self.data_dir)

        summary = context.exception.ingestion_summary

        # Customers should have completed successfully first.
        self.assertEqual(
            summary["olist_customers_dataset.csv"]["status"],
            "success",
        )
        self.assertEqual(
            summary["olist_customers_dataset.csv"]["rows"],
            1,
        )

        # Geolocation should be recorded as failed.
        failed_dataset = summary["olist_geolocation_dataset.csv"]

        self.assertEqual(failed_dataset["status"], "failed")
        self.assertEqual(failed_dataset["rows"], 0)
        self.assertEqual(failed_dataset["chunks"], 0)
        self.assertEqual(failed_dataset["error_type"], "ValueError")
        self.assertIn(
            "Missing required columns",
            failed_dataset["error_message"],
        )

        # Later datasets should not have been processed.
        self.assertEqual(len(summary), 2)

    def test_successfully_ingests_valid_datasets(self):
        for file_name, columns in {
            "olist_geolocation_dataset.csv": [
                "geolocation_zip_code_prefix",
                "geolocation_lat",
                "geolocation_lng",
                "geolocation_city",
                "geolocation_state",
            ],
            "olist_order_items_dataset.csv": [
                "order_id",
                "order_item_id",
                "product_id",
                "seller_id",
                "shipping_limit_date",
                "price",
                "freight_value",
            ],
            "olist_order_payments_dataset.csv": [
                "order_id",
                "payment_sequential",
                "payment_type",
                "payment_installments",
                "payment_value",
            ],
            "olist_order_reviews_dataset.csv": [
                "review_id",
                "order_id",
                "review_score",
                "review_comment_title",
                "review_comment_message",
                "review_creation_date",
                "review_answer_timestamp",
            ],
            "olist_orders_dataset.csv": [
                "order_id",
                "customer_id",
                "order_status",
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            ],
            "olist_products_dataset.csv": [
                "product_id",
                "product_category_name",
                "product_name_lenght",
                "product_description_lenght",
                "product_photos_qty",
                "product_weight_g",
                "product_length_cm",
                "product_height_cm",
                "product_width_cm",
            ],
            "olist_sellers_dataset.csv": [
                "seller_id",
                "seller_zip_code_prefix",
                "seller_city",
                "seller_state",
            ],
            "product_category_name_translation.csv": [
                "product_category_name",
                "product_category_name_english",
            ],
        }.items():
            pd.DataFrame(
                [dict.fromkeys(columns, "sample")]
            ).to_csv(
                self.data_dir / file_name,
                index=False,
            )

        summary = run_ingestion(
            self.data_dir,
            chunk_size=1,
        )

        self.assertEqual(len(summary), 9)
        self.assertEqual(
            summary["olist_customers_dataset.csv"]["rows"],
            1,
        )
        self.assertEqual(
            summary["olist_customers_dataset.csv"]["chunks"],
            1,
        )

    def test_returns_execution_metadata(self):
        # Create the remaining eight registered datasets.
        for file_name, columns in OLIST_SCHEMAS.items():
            if file_name == "olist_customers_dataset.csv":
                continue

            pd.DataFrame(
                [dict.fromkeys(columns, "sample")]
            ).to_csv(
                self.data_dir / file_name,
                index=False,
            )

        summary = run_ingestion(self.data_dir)

        metrics = summary["olist_customers_dataset.csv"]

        self.assertIn("started_at", metrics)
        self.assertIn("completed_at", metrics)
        self.assertIn("duration_seconds", metrics)
        self.assertEqual(metrics["status"], "success")
        self.assertGreaterEqual(metrics["duration_seconds"], 0)




if __name__ == "__main__":
    unittest.main()
