"""Unit tests for the CSV extraction module."""

import tempfile
import unittest
from pathlib import Path

from ingestion.extract import read_csv_in_chunks


class TestReadCSVInChunks(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = Path(self.temp_dir.name) / "sample.csv"
        self.csv_path.write_text(
            "id,name\n"
            "1,Alice\n"
            "2,Bob\n"
            "3,Charlie\n"
            "4,David\n"
            "5,Eve\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_reads_csv_in_chunks(self):
        chunks = list(read_csv_in_chunks(self.csv_path, chunk_size=2))

        self.assertEqual([len(chunk) for chunk in chunks], [2, 2, 1])
        self.assertEqual(sum(len(chunk) for chunk in chunks), 5)

    def test_rejects_zero_chunk_size(self):
        with self.assertRaises(ValueError):
            read_csv_in_chunks(self.csv_path, chunk_size=0)

    def test_rejects_negative_chunk_size(self):
        with self.assertRaises(ValueError):
            read_csv_in_chunks(self.csv_path, chunk_size=-1)

    def test_raises_error_for_missing_file(self):
        missing_path = Path(self.temp_dir.name) / "missing.csv"

        with self.assertRaises(FileNotFoundError):
            read_csv_in_chunks(missing_path)

    def test_rejects_non_csv_file(self):
        text_path = Path(self.temp_dir.name) / "sample.txt"
        text_path.write_text("sample data", encoding="utf-8")

        with self.assertRaises(ValueError):
            read_csv_in_chunks(text_path)


if __name__ == "__main__":
    unittest.main()
