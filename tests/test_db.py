"""Tests for managing db"""
import pytest
import sqlite3
import tempfile
from whatsup.db import DataBase
from whatsup.tasks import InitTaskTables


@pytest.fixture(scope="function")
def get_connection():
    tmpfilename = tempfile.NamedTemporaryFile(mode="w")
    db_name = tmpfilename.name
    conn = sqlite3.connect(db_name)
    yield conn, db_name
    tmpfilename.close()


query_tables = """SELECT name FROM sqlite_master
    WHERE type='table' and not name like 'sqlite%'"""


def cnt_tables(conn, query=query_tables):
    return len(conn.execute(query).fetchall())


def test_create_table(get_connection):
    """Test that we can create tables and drop them"""
    conn, db_name = get_connection
    db = DataBase(db_name)
    db.create_table("test_table1", ["col1 int", "col2 varchar"])
    db.create_table("test_table2", ["col1 int", "col2 varchar"])

    assert cnt_tables(conn) == 2
    db.truncate_table("test_table1")  # doesn't delete table
    assert cnt_tables(conn) == 2
    db.drop_table("test_table1")
    assert cnt_tables(conn) == 1
    db.drop_table("test_table2")
    assert cnt_tables(conn) == 0


def test_init_default_tables(get_connection):
    """Test that we can create tables. Might move it to test_tasks"""
    conn, db_name = get_connection
    db = DataBase(db_name)
    init_tables = InitTaskTables(db)
    init_tables.archived_tasks()
    init_tables.active_tasks()

    assert cnt_tables(conn) == 2
    InitTaskTables(db, is_drop=True)  # rewrite, no new tables
    assert cnt_tables(conn) == 2


def test_add_record(get_connection):
    conn, db_name = get_connection
    db = DataBase(db_name)
    db.create_table("test_table1", ["col1 int"])

    def fetch_from_table(tablename, conn=conn):
        return conn.execute(f"select * from {tablename}").fetchall()

    assert len(fetch_from_table("test_table1")) == 0
    db.add_record("test_table1", {"col1": 1})
    assert len(fetch_from_table("test_table1")) == 1
    db.add_record("test_table1", {"col1": 2})

    # test fetch records separately
    assert db.fetch_records("test_table1") == [{"col1": 1}, {"col1": 2}]
    assert len(fetch_from_table("test_table1")) == 2
    # test update record separately
    db.update_record("test_table1", value={"col1": 100}, filter="col1=1")
    assert db.fetch_records("test_table1") == [{"col1": 100}, {"col1": 2}]
    # test delete record separately
    db.delete_record("test_table1", filter="col1=2")
    assert db.fetch_records("test_table1") == [{"col1": 100}]

    db.truncate_table("test_table1")
    assert len(fetch_from_table("test_table1")) == 0


def test_fetch():
    ...


def test_update():
    ...


def test_delete():
    ...
