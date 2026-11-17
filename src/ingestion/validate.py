"""Validation functions for ingested datasets."""

import pandas as pd
from ingestion.schemas import OLIST_SCHEMAS


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
) -> None:
    """Ensure that a DataFrame contains all required columns."""

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def validate_not_empty(df: pd.DataFrame) -> None:
    """Ensure that a DataFrame contains at least one row."""

    if df.empty:
        raise ValueError("Dataset is empty.")


def validate_no_nulls(
    df: pd.DataFrame,
    required_columns: list[str],
) -> None:
    """Ensure that specified required columns contain no null values."""

    validate_required_columns(df, required_columns)

    null_counts = df[required_columns].isnull().sum()
    columns_with_nulls = null_counts[null_counts > 0]

    if not columns_with_nulls.empty:
        raise ValueError(
            f"Null values found in required columns: "
            f"{columns_with_nulls.to_dict()}"
        )


def validate_source_schema(
    df: pd.DataFrame,
    file_name: str,
) -> None:
    """Validate a source DataFrame against its registered schema."""

    if file_name not in OLIST_SCHEMAS:
        raise ValueError(
            f"No registered schema found for: {file_name}"
        )

    validate_required_columns(
        df,
        OLIST_SCHEMAS[file_name],
    )