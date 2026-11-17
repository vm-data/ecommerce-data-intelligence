"""Orchestration for the source data ingestion pipeline."""

from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from ingestion.config import OLIST_RAW_DIR
from ingestion.extract import read_csv_in_chunks
from ingestion.schemas import OLIST_SCHEMAS
from ingestion.validate import (
    validate_not_empty,
    validate_source_schema,
)


class IngestionError(Exception):
    """Raised when a dataset fails during ingestion."""

    def __init__(
        self,
        message: str,
        ingestion_summary: dict,
    ) -> None:
        super().__init__(message)
        self.ingestion_summary = ingestion_summary


def run_ingestion(
    data_directory: Path = OLIST_RAW_DIR,
    chunk_size: int = 100_000,
) -> dict[str, dict[str, int | float | str]]:
    """Read and validate all registered source datasets."""

    if not data_directory.is_dir():
        raise FileNotFoundError(
            f"Data directory not found: {data_directory}"
        )

    discovered_files = {
        path.name: path
        for path in data_directory.glob("*.csv")
    }

    expected_files = set(OLIST_SCHEMAS)
    discovered_names = set(discovered_files)

    missing_files = sorted(expected_files - discovered_names)
    unexpected_files = sorted(discovered_names - expected_files)

    if missing_files:
        raise FileNotFoundError(
            f"Missing expected datasets: {missing_files}"
        )

    if unexpected_files:
        raise ValueError(
            f"Unregistered datasets found: {unexpected_files}"
        )

    ingestion_summary = {}

    for file_name in sorted(expected_files):
        file_path = discovered_files[file_name]

        started_at = datetime.now(UTC)
        start_time = perf_counter()

        total_rows = 0
        total_chunks = 0

        try:
            for chunk in read_csv_in_chunks(
                file_path,
                chunk_size=chunk_size,
            ):
                validate_not_empty(chunk)
                validate_source_schema(chunk, file_name)

                total_rows += len(chunk)
                total_chunks += 1

            if total_chunks == 0:
                raise ValueError(
                    f"Dataset contains no rows: {file_name}"
                )

        except Exception as error:
            completed_at = datetime.now(UTC)
            duration = perf_counter() - start_time

            ingestion_summary[file_name] = {
                "rows": total_rows,
                "chunks": total_chunks,
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_seconds": round(duration, 3),
                "status": "failed",
                "error_type": type(error).__name__,
                "error_message": str(error),
            }

            raise IngestionError(
                f"Ingestion failed for {file_name}: {error}",
                ingestion_summary,
            ) from error

        completed_at = datetime.now(UTC)
        duration = perf_counter() - start_time

        ingestion_summary[file_name] = {
            "rows": total_rows,
            "chunks": total_chunks,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_seconds": round(duration, 3),
            "status": "success",
        }

    return ingestion_summary