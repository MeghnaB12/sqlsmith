"""Tests for the read-only SQL safety layer."""

import pytest

from app.sql.safety import UnsafeSQLError, ensure_read_only


def test_plain_select_gets_a_limit() -> None:
    out = ensure_read_only("SELECT * FROM customers", max_rows=50)
    assert "LIMIT 50" in out.upper()


def test_existing_limit_is_preserved() -> None:
    out = ensure_read_only("SELECT * FROM customers LIMIT 5", max_rows=50)
    assert "LIMIT 5" in out.upper()
    assert "LIMIT 50" not in out.upper()


def test_delete_is_rejected() -> None:
    with pytest.raises(UnsafeSQLError):
        ensure_read_only("DELETE FROM customers", max_rows=50)


def test_stacked_statements_are_rejected() -> None:
    with pytest.raises(UnsafeSQLError):
        ensure_read_only("SELECT 1; DROP TABLE customers", max_rows=50)


def test_ddl_is_rejected() -> None:
    with pytest.raises(UnsafeSQLError):
        ensure_read_only("DROP TABLE customers", max_rows=50)


def test_garbage_is_rejected() -> None:
    with pytest.raises(UnsafeSQLError):
        ensure_read_only("not sql at all ((", max_rows=50)
