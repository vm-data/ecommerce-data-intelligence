"""Command-line entry point for the Olist ingestion pipeline."""

import sys
from pathlib import Path
from time import perf_counter

from ingestion.config import INGESTION_METADATA_DIR, OLIST_RAW_DIR
from ingestion.metadata import save_ingestion_metadata
from ingestion.pipeline import IngestionError, run_ingestion


def main(
    data_directory: Path = OLIST_RAW_DIR,
    metadata_directory: Path = INGESTION_METADATA_DIR,
) -> None:
    """Run ingestion and print a summary."""

    pipeline_started = perf_counter()

    print("Starting Olist data ingestion...\n")

    ingestion_succeeded = True

    try:
        summary = run_ingestion(data_directory)
    except IngestionError as error:
        ingestion_succeeded = False
        summary = error.ingestion_summary

        print(f"Ingestion failed: {error}\n")

    metadata_path = save_ingestion_metadata(
    summary,
    metadata_directory,
    )

    total_rows = 0

    print("Ingestion results")
    print("-" * 75)

    for file_name, metrics in summary.items():
        rows = metrics["rows"]
        chunks = metrics["chunks"]
        duration = metrics["duration_seconds"]
        status = metrics["status"]

        total_rows += rows

        print(
            f"{file_name:<45} "
            f"Rows: {rows:>10,} | "
            f"Chunks: {chunks:>3} | "
            f"Time: {duration:>6.3f}s | "
            f"{status.upper()}"
        )

        if status == "failed":
            print(
                f"  Error: {metrics['error_type']}: "
                f"{metrics['error_message']}"
            )

    total_duration = perf_counter() - pipeline_started

    print("-" * 75)
    print(f"Datasets processed: {len(summary)}")
    print(f"Total rows ingested: {total_rows:,}")
    print(f"Total execution time: {total_duration:.3f} seconds")
    print(f"Metadata saved to: {metadata_path}")

    if not ingestion_succeeded:
        print("\nIngestion completed with errors.")
        sys.exit(1)

    print("\nIngestion completed successfully.")


if __name__ == "__main__":
    main()