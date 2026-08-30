"""Ephemeral in-memory sandbox database.

Each request gets a fresh in-memory DuckDB seeded with a small sample dataset.
Because it's rebuilt per request and thrown away, plus the safety layer blocks
any non-SELECT, there's nothing a generated query can damage.
"""

from typing import Any

import duckdb

_SEED = """
CREATE TABLE customers (
    id       INTEGER,
    name     VARCHAR,
    country  VARCHAR,
    created  DATE
);
INSERT INTO customers VALUES
    (1, 'Ada Lovelace',   'UK',    DATE '2023-01-04'),
    (2, 'Alan Turing',    'UK',    DATE '2023-02-11'),
    (3, 'Grace Hopper',   'US',    DATE '2023-03-20'),
    (4, 'Katherine Johnson', 'US', DATE '2023-05-02');

CREATE TABLE orders (
    id           INTEGER,
    customer_id  INTEGER,
    amount       DECIMAL(10,2),
    placed       DATE
);
INSERT INTO orders VALUES
    (1, 1, 49.90,  DATE '2023-06-01'),
    (2, 1, 12.00,  DATE '2023-06-15'),
    (3, 3, 150.00, DATE '2023-07-04'),
    (4, 4, 22.50,  DATE '2023-07-19');
"""


def new_connection() -> duckdb.DuckDBPyConnection:
    """Return a fresh in-memory DuckDB seeded with the sample dataset."""
    con = duckdb.connect(database=":memory:")
    con.execute(_SEED)
    return con


def describe_schema(con: duckdb.DuckDBPyConnection) -> str:
    """Return a compact text schema for prompt injection."""
    rows = con.execute(
        """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'main'
        ORDER BY table_name, ordinal_position
        """
    ).fetchall()

    tables: dict[str, list[str]] = {}
    for table_name, column_name, data_type in rows:
        tables.setdefault(table_name, []).append(f"{column_name} {data_type}")

    return "\n".join(f"{table} ({', '.join(cols)})" for table, cols in tables.items())


def run_query(con: duckdb.DuckDBPyConnection, sql: str) -> list[dict[str, Any]]:
    """Execute an already-validated read-only query and return rows as dicts."""
    cursor = con.execute(sql)
    columns = [d[0] for d in cursor.description]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]
