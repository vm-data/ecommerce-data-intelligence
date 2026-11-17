
"""Utilities for persisting ingestion run metadata."""

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ingestion.config import INGESTION_METADATA_DIR


def save_ingestion_metadata(
    ingestion_summary: dict,
    output_directory: Path = INGESTION_METADATA_DIR,
) -> Path:
    """Save an ingestion run summary as a JSON manifest."""
    if not ingestion_summary:
        raise ValueError(
            "Cannot save metadata for an empty ingestion summary."
        )

    output_directory.mkdir(parents=True, exist_ok=True)

    run_started_at = min(
        metrics["started_at"]
        for metrics in ingestion_summary.values()
    )

    run_completed_at = max(
        metrics["completed_at"]
        for metrics in ingestion_summary.values()
    )

    total_rows = sum(
        metrics["rows"]
        for metrics in ingestion_summary.values()
    )

    total_duration = sum(
        metrics["duration_seconds"]
        for metrics in ingestion_summary.values()
    )

    run_id = (
        f"ingestion_run_"
        f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%S')}_"
        f"{uuid4().hex[:8]}"
    )

    manifest = {
        "run_id": run_id,
        "started_at": run_started_at,
        "completed_at": run_completed_at,
        "total_rows": total_rows,
        "total_datasets": len(ingestion_summary),
        "total_dataset_duration_seconds": round(total_duration, 3),
        "datasets": ingestion_summary,
    }

    output_path = output_directory / f"{run_id}.json"

    with output_path.open("x", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)

    return output_path
