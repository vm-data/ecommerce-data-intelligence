"""Functions for extracting data from CSV source files."""

from pathlib import Path
from typing import Iterator

import pandas as pd


def read_csv_in_chunks(
    file_path: Path,
    chunk_size: int = 100_000,
) -> Iterator[pd.DataFrame]:
    """Read a CSV file in manageable chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if not file_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    if file_path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a CSV file: {file_path}")

    return pd.read_csv(file_path, chunksize=chunk_size)
