
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL


# Locate the project root and load environment variables.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def get_engine() -> Engine:
    """Create and return a SQLAlchemy engine for PostgreSQL."""

    required_variables = [
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        raise RuntimeError(
            f"Missing database environment variables: {missing_variables}"
        )

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host="localhost",
        port=5432,
        database=os.getenv("POSTGRES_DB"),
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    return engine


def test_connection() -> None:
    """Test connectivity to PostgreSQL."""

    engine = get_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(
                    """
                    SELECT
                        current_database(),
                        current_user,
                        version();
                    """
                )
            )

            database, user, version = result.fetchone()

            print("PostgreSQL connection successful!")
            print(f"Database: {database}")
            print(f"User: {user}")
            print(f"Version: {version}")

    finally:
        engine.dispose()
