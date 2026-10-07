"""Reusable helpers for loading and querying the project PostgreSQL database."""

import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL


def create_postgres_engine() -> Engine:
    """Create a PostgreSQL engine from DB_* variables or the project .env file."""
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    required = ("DB_USER", "DB_PASSWORD", "DB_NAME")
    missing = [name for name in required if name not in os.environ]
    if missing:
        raise ValueError(
            "Missing required database environment variables: "
            + ", ".join(missing)
        )

    try:
        port = int(os.environ.get("DB_PORT", "5432"))
    except ValueError as exc:
        raise ValueError("DB_PORT must be an integer.") from exc
    if not 1 <= port <= 65535:
        raise ValueError("DB_PORT must be between 1 and 65535.")

    url = URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ.get("DB_HOST", "localhost"),
        port=port,
        database=os.environ["DB_NAME"],
    )
    return create_engine(url, pool_pre_ping=True)


def load_csv_to_postgres(
    csv_path: str | Path,
    engine: Engine,
    table_name: str,
    *,
    if_exists: Literal["fail", "replace", "append"] = "fail",
    chunksize: int = 1000,
) -> int:
    """Load a CSV into PostgreSQL and return the number of submitted rows."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise ValueError("table_name must be a simple SQL identifier.")
    if if_exists not in {"fail", "replace", "append"}:
        raise ValueError("if_exists must be 'fail', 'replace', or 'append'.")
    if chunksize < 1:
        raise ValueError("chunksize must be a positive integer.")

    dataframe = pd.read_csv(csv_path)
    dataframe.to_sql(
        name=table_name,
        con=engine,
        if_exists=if_exists,
        index=False,
        chunksize=chunksize,
        method="multi",
    )
    return len(dataframe)


def read_sql_dataframe(
    engine: Engine,
    query: str,
    params: Mapping[str, object] | None = None,
) -> pd.DataFrame:
    """Execute one SQLAlchemy text query and return its results as a DataFrame."""
    return pd.read_sql_query(text(query), con=engine, params=params)
