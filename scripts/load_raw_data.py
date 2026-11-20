"""Command-line entry point for loading Olist data into PostgreSQL."""

from storage.loader import load_all_datasets


def main():
    results = load_all_datasets()

    print("\n" + "=" * 55)
    print("RAW DATA LOADING SUMMARY")
    print("=" * 55)

    total_rows = 0

    for table_name, row_count in results.items():
        print(f"{table_name:<40} {row_count:>12,}")
        total_rows += row_count

    print("-" * 55)
    print(f"{'TOTAL':<40} {total_rows:>12,}")
    print("=" * 55)


if __name__ == "__main__":
    main()
