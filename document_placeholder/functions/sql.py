from __future__ import annotations

import sqlite3

from document_placeholder.functions import FunctionRegistry

_db_path: str = "data.db"
_connection: sqlite3.Connection | None = None


def init(db_path: str = "data.db") -> None:
    """Set the database path (call before evaluating any expressions)."""
    global _db_path, _connection
    _db_path = db_path
    _connection = None


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(_db_path)
    return _connection


def close() -> None:
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None


@FunctionRegistry.register("SQL")
def sql(query: str):
    """Execute a SQL query and return the result.

    * ``SELECT`` → first column of first row (or ``None``)
    * Everything else → ``None`` (side-effect only)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)

    upper = query.strip().upper()
    if upper.startswith("SELECT"):
        row = cursor.fetchone()
        conn.commit()
        if row is None:
            return None
        return row[0] if len(row) == 1 else row

    conn.commit()
    return None
