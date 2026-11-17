"""Central configuration for the data ingestion package."""

from pathlib import Path


# Project directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

# Olist source dataset directory
OLIST_RAW_DIR = RAW_DATA_DIR / "olist"

# Ingestion metadata directory
INGESTION_METADATA_DIR = DATA_DIR / "metadata" / "ingestion"
