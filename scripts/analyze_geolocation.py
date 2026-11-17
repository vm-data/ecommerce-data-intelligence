from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

GEOLOCATION_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "olist"
    / "olist_geolocation_dataset.csv"
)


def main():
    """Analyze geolocation records and postal-code cardinality."""

    df = pd.read_csv(GEOLOCATION_PATH)

    zip_column = "geolocation_zip_code_prefix"

    # Count records for each postal-code prefix
    records_per_zip = df.groupby(zip_column).size()

    # Count distinct coordinate pairs for each prefix
    coordinates_per_zip = (
        df.groupby(zip_column)[
            ["geolocation_lat", "geolocation_lng"]
        ]
        .apply(lambda group: group.drop_duplicates().shape[0])
    )

    print("\nGEOLOCATION DATASET ANALYSIS")
    print("=" * 65)

    print(f"Total rows: {len(df):,}")
    print(f"Unique postal-code prefixes: {df[zip_column].nunique():,}")
    print(f"Exact duplicate rows: {df.duplicated().sum():,}")

    print("\nPOSTAL-CODE PREFIX CARDINALITY")
    print("=" * 65)

    print(
        f"Prefixes with multiple records: "
        f"{(records_per_zip > 1).sum():,}"
    )

    print(
        f"Prefixes with multiple distinct coordinate pairs: "
        f"{(coordinates_per_zip > 1).sum():,}"
    )

    print(
        f"Maximum records for one prefix: "
        f"{records_per_zip.max():,}"
    )

    print(
        f"Maximum distinct coordinate pairs for one prefix: "
        f"{coordinates_per_zip.max():,}"
    )

    print("\nTOP 10 PREFIXES BY RECORD COUNT")
    print("=" * 65)

    print(records_per_zip.sort_values(ascending=False).head(10).to_string())


if __name__ == "__main__":
    main()