"""Tests for the SQL function (uses an in-memory SQLite database)."""

from __future__ import annotations

import pytest

import document_placeholder.functions.sql as sql_mod

from document_placeholder.functions import FunctionRegistry

call = FunctionRegistry.call


@pytest.fixture(autouse=True)
def _use_memory_db():
    """Use a fresh in-memory database for every test."""
    sql_mod.init(":memory:")
    yield
    sql_mod.close()


class TestSqlCreateAndInsert:

    def test_create_table(self):
        result = call("SQL", ["CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT)"])
        assert result is None

    def test_insert(self):
        call("SQL", ["CREATE TABLE t (id INTEGER PRIMARY KEY, val INTEGER)"])
        result = call("SQL", ["INSERT INTO t (val) VALUES (42)"])
        assert result is None

    def test_insert_and_select(self):
        call("SQL", ["CREATE TABLE t (id INTEGER PRIMARY KEY, val INTEGER)"])
        call("SQL", ["INSERT INTO t (val) VALUES (99)"])
        assert call("SQL", ["SELECT val FROM t WHERE id = 1"]) == 99


class TestSqlSelect:

    def test_single_column(self):
        call("SQL", ["CREATE TABLE t (v TEXT)"])
        call("SQL", ["INSERT INTO t VALUES ('hello')"])
        assert call("SQL", ["SELECT v FROM t"]) == "hello"

    def test_multi_column_returns_tuple(self):
        call("SQL", ["CREATE TABLE t (a INTEGER, b TEXT)"])
        call("SQL", ["INSERT INTO t VALUES (1, 'x')"])
        result = call("SQL", ["SELECT a, b FROM t"])
        assert result == (1, "x")

    def test_empty_result(self):
        call("SQL", ["CREATE TABLE t (v INTEGER)"])
        assert call("SQL", ["SELECT v FROM t"]) is None


class TestSqlUpdate:

    def test_update(self):
        call("SQL", ["CREATE TABLE t (v INTEGER)"])
        call("SQL", ["INSERT INTO t VALUES (1)"])
        call("SQL", ["UPDATE t SET v = 42"])
        assert call("SQL", ["SELECT v FROM t"]) == 42


class TestSqlDelete:

    def test_delete(self):
        call("SQL", ["CREATE TABLE t (v INTEGER)"])
        call("SQL", ["INSERT INTO t VALUES (1)"])
        call("SQL", ["INSERT INTO t VALUES (2)"])
        call("SQL", ["DELETE FROM t WHERE v = 1"])
        assert call("SQL", ["SELECT v FROM t"]) == 2


class TestSqlConnectionManagement:

    def test_init_resets_connection(self):
        sql_mod.init(":memory:")
        conn1 = sql_mod.get_connection()
        sql_mod.init(":memory:")
        conn2 = sql_mod.get_connection()
        assert conn1 is not conn2

    def test_close_and_reopen(self):
        call("SQL", ["CREATE TABLE t (v INTEGER)"])
        call("SQL", ["INSERT INTO t VALUES (1)"])
        sql_mod.close()
        sql_mod.init(":memory:")
        call("SQL", ["CREATE TABLE t (v INTEGER)"])
        assert call("SQL", ["SELECT v FROM t"]) is None
