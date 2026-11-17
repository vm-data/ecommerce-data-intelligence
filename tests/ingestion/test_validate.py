"""Unit tests for dataset validation."""

import unittest

import pandas as pd

from ingestion.validate import (
    validate_no_nulls,
    validate_not_empty,
    validate_required_columns,
    validate_source_schema,
)

class TestValidateRequiredColumns(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame(
            {
                "customer_id": ["C001", "C002"],
                "customer_city": ["Sao Paulo", "Rio de Janeiro"],
                "customer_state": ["SP", "RJ"],
            }
        )

    def test_passes_when_all_required_columns_exist(self):
        required_columns = [
            "customer_id",
            "customer_city",
            "customer_state",
        ]

        result = validate_required_columns(
            self.df,
            required_columns,
        )

        self.assertIsNone(result)

    def test_fails_when_required_column_is_missing(self):
        required_columns = [
            "customer_id",
            "customer_city",
            "customer_state",
            "customer_zip_code_prefix",
        ]

        with self.assertRaisesRegex(
            ValueError,
            "customer_zip_code_prefix",
        ):
            validate_required_columns(
                self.df,
                required_columns,
            )

    def test_reports_all_missing_columns(self):
        required_columns = [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
        ]

        with self.assertRaises(ValueError) as context:
            validate_required_columns(
                self.df,
                required_columns,
            )

        error_message = str(context.exception)

        self.assertIn("customer_unique_id", error_message)
        self.assertIn("customer_zip_code_prefix", error_message)

    def test_passes_when_dataframe_contains_rows(self):
        result = validate_not_empty(self.df)
        self.assertIsNone(result)

    def test_fails_when_dataframe_is_empty(self):
        empty_df = pd.DataFrame()

        with self.assertRaisesRegex(
            ValueError,
            "Dataset is empty",
        ):
            validate_not_empty(empty_df)

    def test_passes_when_required_columns_have_no_nulls(self):
        required_columns = [
            "customer_id",
            "customer_city",
        ]

        result = validate_no_nulls(
            self.df,
            required_columns,
        )

        self.assertIsNone(result)

    def test_fails_when_required_column_contains_nulls(self):
        df_with_nulls = self.df.copy()
        df_with_nulls.loc[0, "customer_id"] = None

        with self.assertRaisesRegex(
            ValueError,
            "customer_id",
        ):
            validate_no_nulls(
                df_with_nulls,
                ["customer_id"],
            )

    def test_allows_nulls_in_optional_columns(self):
        df_with_nulls = self.df.copy()
        df_with_nulls["optional_field"] = [None, "value"]

        result = validate_no_nulls(
            df_with_nulls,
            ["customer_id", "customer_city"],
        )

        self.assertIsNone(result)


class TestValidateSourceSchema(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame(
            {
                "customer_id": ["C001"],
                "customer_unique_id": ["U001"],
                "customer_zip_code_prefix": ["01001"],
                "customer_city": ["Sao Paulo"],
                "customer_state": ["SP"],
            }
        )

    def test_passes_for_valid_source_schema(self):
        result = validate_source_schema(
            self.df,
            "olist_customers_dataset.csv",
        )

        self.assertIsNone(result)

    def test_fails_when_source_column_is_missing(self):
        invalid_df = self.df.drop(columns=["customer_city"])

        with self.assertRaisesRegex(
            ValueError,
            "customer_city",
        ):
            validate_source_schema(
                invalid_df,
                "olist_customers_dataset.csv",
            )

    def test_fails_for_unregistered_dataset(self):
        with self.assertRaisesRegex(
            ValueError,
            "No registered schema found",
        ):
            validate_source_schema(
                self.df,
                "unknown_dataset.csv",
            )


if __name__ == "__main__":
    unittest.main()
