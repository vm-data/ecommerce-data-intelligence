
from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw" / "olist"


def profile_dataset(dataset_path: Path) -> None:
    """Display a basic data-quality and structure profile."""

    df = pd.read_csv(dataset_path)

    print("\n" + "=" * 70)
    print(f"DATASET: {dataset_path.name}")
    print("=" * 70)

    # Dataset dimensions
    print(f"\nRows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")

    # Column names and data types
    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes.to_string())

    # Missing values
    print("\nMissing values:")
    missing_values = df.isnull().sum()
    print(missing_values.to_string())

    # Duplicate records
    print(f"\nDuplicate rows: {df.duplicated().sum():,}")


def main():
    """Discover and profile all CSV datasets."""

    if not DATA_DIRECTORY.exists():
        raise FileNotFoundError(
            f"Data directory not found: {DATA_DIRECTORY}"
        )

    csv_files = sorted(DATA_DIRECTORY.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in: {DATA_DIRECTORY}"
        )

    print(f"Found {len(csv_files)} CSV datasets.")

    for dataset_path in csv_files:
        profile_dataset(dataset_path)


if __name__ == "__main__":
    main()
