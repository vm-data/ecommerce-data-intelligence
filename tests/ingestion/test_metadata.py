
"""Tests for ingestion metadata persistence."""

import json
import tempfile
import unittest
from pathlib import Path

from ingestion.metadata import save_ingestion_metadata


class TestIngestionMetadata(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)

        self.sample_summary = {
            "customers.csv": {
                "rows": 100,
                "chunks": 1,
                "started_at": "2026-11-16T10:00:00+00:00",
                "completed_at": "2026-11-16T10:00:01+00:00",
                "duration_seconds": 1.0,
                "status": "success",
            },
            "orders.csv": {
                "rows": 200,
                "chunks": 2,
                "started_at": "2026-11-16T10:00:01+00:00",
                "completed_at": "2026-11-16T10:00:03+00:00",
                "duration_seconds": 2.0,
                "status": "success",
            },
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_creates_json_manifest(self):
        output_path = save_ingestion_metadata(
            self.sample_summary,
            self.output_dir,
        )

        self.assertTrue(output_path.is_file())
        self.assertEqual(output_path.suffix, ".json")

    def test_manifest_contains_correct_totals(self):
        output_path = save_ingestion_metadata(
            self.sample_summary,
            self.output_dir,
        )

        with output_path.open(encoding="utf-8") as file:
            manifest = json.load(file)

        self.assertEqual(manifest["total_rows"], 300)
        self.assertEqual(manifest["total_datasets"], 2)
        self.assertEqual(
            manifest["total_dataset_duration_seconds"],
            3.0,
        )

    def test_manifest_contains_dataset_details(self):
        output_path = save_ingestion_metadata(
            self.sample_summary,
            self.output_dir,
        )

        with output_path.open(encoding="utf-8") as file:
            manifest = json.load(file)

        self.assertIn("customers.csv", manifest["datasets"])
        self.assertIn("orders.csv", manifest["datasets"])

    def test_manifest_preserves_failed_dataset_details(self):
        failed_summary = {
            "customers.csv": {
                "rows": 100,
                "chunks": 1,
                "started_at": "2026-11-16T10:00:00+00:00",
                "completed_at": "2026-11-16T10:00:01+00:00",
                "duration_seconds": 1.0,
                "status": "success",
            },
            "orders.csv": {
                "rows": 50,
                "chunks": 1,
                "started_at": "2026-11-16T10:00:01+00:00",
                "completed_at": "2026-11-16T10:00:02+00:00",
                "duration_seconds": 1.0,
                "status": "failed",
                "error_type": "ValueError",
                "error_message": "Missing required columns",
            },
        }

        output_path = save_ingestion_metadata(
            failed_summary,
            self.output_dir,
        )

        with output_path.open(encoding="utf-8") as file:
            manifest = json.load(file)

        failed_dataset = manifest["datasets"]["orders.csv"]

        self.assertEqual(failed_dataset["status"], "failed")
        self.assertEqual(failed_dataset["rows"], 50)
        self.assertEqual(failed_dataset["chunks"], 1)
        self.assertEqual(failed_dataset["error_type"], "ValueError")
        self.assertEqual(
            failed_dataset["error_message"],
            "Missing required columns",
        )

        self.assertEqual(manifest["total_rows"], 150)
        self.assertEqual(manifest["total_datasets"], 2)

    def test_rejects_empty_summary(self):
        with self.assertRaisesRegex(
            ValueError,
            "empty ingestion summary",
        ):
            save_ingestion_metadata({}, self.output_dir)


if __name__ == "__main__":
    unittest.main()
