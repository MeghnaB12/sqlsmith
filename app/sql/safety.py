"""Read-only SQL safety layer.

The model is not trusted. Before any generated SQL touches the database we
parse it with sqlglot and prove three things:

1. It is exactly one statement (no stacked ``SELECT ...; DROP ...``).
2. Its root is a read-only query (SELECT or a set operation).
3. It contains no DML/DDL/command nodes anywhere in the tree.

A plain SELECT with no LIMIT gets one appended, so a careless query can't
try to stream a whole table back.
"""

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

# Statement roots we consider read-only.
_ALLOWED_ROOTS = (exp.Select, exp.Union, exp.Intersect, exp.Except)

# Anything from this set appearing anywhere means the query is rejected.
_FORBIDDEN = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Create,
    exp.Alter,
    exp.Command,  # PRAGMA, SET, CALL, COPY, ATTACH, ...
    exp.Merge,
)


class UnsafeSQLError(ValueError):
    """Raised when generated SQL is not a safe, single, read-only query."""


def ensure_read_only(sql: str, *, max_rows: int, dialect: str = "duckdb") -> str:
    """Validate ``sql`` is a single read-only query and return a safe form.

    Raises:
        UnsafeSQLError: if the SQL can't be parsed or isn't read-only.
    """
    try:
        parsed = [stmt for stmt in sqlglot.parse(sql, dialect=dialect) if stmt is not None]
    except ParseError as exc:
        raise UnsafeSQLError(f"could not parse SQL: {exc}") from exc

    if len(parsed) != 1:
        raise UnsafeSQLError("exactly one SQL statement is allowed")

    statement = parsed[0]

    if not isinstance(statement, _ALLOWED_ROOTS):
        raise UnsafeSQLError(f"only read-only queries are allowed, got {type(statement).__name__}")

    if any(True for _ in statement.find_all(*_FORBIDDEN)):
        raise UnsafeSQLError("statement contains a non-read-only operation")

    # Append a LIMIT to a bare SELECT so results are always bounded.
    if isinstance(statement, exp.Select) and statement.args.get("limit") is None:
        statement = statement.limit(max_rows)

    return str(statement.sql(dialect=dialect))
