
"""Tests for the ingestion command-line runner."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd

from ingestion.schemas import OLIST_SCHEMAS
from scripts.run_ingestion import main


class TestIngestionRunner(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)

        self.data_dir = self.base_dir / "raw"
        self.metadata_dir = self.base_dir / "metadata"

        self.data_dir.mkdir()

        # Create all registered datasets.
        for file_name, columns in OLIST_SCHEMAS.items():

            if file_name == "olist_geolocation_dataset.csv":
                # Deliberately introduce a schema error.
                data = pd.DataFrame(
                    {"wrong_column": ["sample"]}
                )

            else:
                data = pd.DataFrame(
                    [dict.fromkeys(columns, "sample")]
                )

            data.to_csv(
                self.data_dir / file_name,
                index=False,
            )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_saves_failure_metadata_and_exits_with_error(self):
        output = io.StringIO()

        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as context:
                main(
                    data_directory=self.data_dir,
                    metadata_directory=self.metadata_dir,
                )

        # The runner must signal failure to the operating system.
        self.assertEqual(context.exception.code, 1)

        # A failure manifest must have been saved.
        manifest_files = list(self.metadata_dir.glob("*.json"))
        self.assertEqual(len(manifest_files), 1)

        with manifest_files[0].open(encoding="utf-8") as file:
            manifest = json.load(file)

        datasets = manifest["datasets"]

        # Customers succeeded before geolocation failed.
        self.assertEqual(
            datasets["olist_customers_dataset.csv"]["status"],
            "success",
        )

        failed_dataset = datasets["olist_geolocation_dataset.csv"]

        self.assertEqual(failed_dataset["status"], "failed")
        self.assertEqual(failed_dataset["error_type"], "ValueError")
        self.assertIn(
            "Missing required columns",
            failed_dataset["error_message"],
        )

        # Only the two datasets reached before failure are recorded.
        self.assertEqual(manifest["total_datasets"], 2)

        # The runner should report the failure to the console.
        self.assertIn("Ingestion failed", output.getvalue())
        self.assertIn(
            "Ingestion completed with errors",
            output.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
