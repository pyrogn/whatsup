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


def test_create_table(get_connection):
    """Test that we can create tables and drop them"""
    conn, db_name = get_connection
    db = DataBase(db_name)
    db.create_table("test_table1", ["col1 int", "col2 varchar"])
    db.create_table("test_table2", ["col1 int", "col2 varchar"])
    query = """SELECT name FROM sqlite_master WHERE type='table'"""

    def cnt_tables(query=query, conn=conn):
        return len(conn.execute(query).fetchall())

    assert cnt_tables() == 2
    db.truncate_table("test_table1")  # doesn't delete table
    assert cnt_tables() == 2
    db.drop_table("test_table1")
    assert cnt_tables() == 1
    db.drop_table("test_table2")
    assert cnt_tables() == 0


def test_init_default_tables(get_connection):
    """Test that we can create tables. Might move it to test_tasks"""
    conn, db_name = get_connection
    db = DataBase(db_name)
    init_tables = InitTaskTables(db)
    init_tables.archived_tasks()
    init_tables.active_tasks()
    query = """SELECT name FROM sqlite_master
    WHERE type='table' and not name like 'sqlite%'"""

    def cnt_tables(query=query, conn=conn):
        return len(conn.execute(query).fetchall())

    assert cnt_tables() == 2
    InitTaskTables(db, is_drop=True)  # rewrite
    assert cnt_tables() == 2


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
    assert len(fetch_from_table("test_table1")) == 2
    db.truncate_table("test_table1")
    assert len(fetch_from_table("test_table1")) == 0


def test_select_fetch():
    ...


def test_update():
    ...


def test_delete():
    ...
