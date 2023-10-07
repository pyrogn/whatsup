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


def test_create_db(get_connection):
    """Test that we can create tables and drop them"""
    conn, db_name = get_connection
    db = DataBase(db_name)
    db.create_table("test_table1", ["col1 int", "col2 varchar"])
    db.create_table("test_table2", ["col1 int", "col2 varchar"])
    query = """SELECT name FROM sqlite_master
    WHERE type='table'"""
    assert len(conn.execute(query).fetchall()) == 2
    db.truncate_table("test_table1")
    assert len(conn.execute(query).fetchall()) == 2
    db.drop_table("test_table1")
    assert len(conn.execute(query).fetchall()) == 1
    db.drop_table("test_table2")
    assert len(conn.execute(query).fetchall()) == 0


def test_create_table():
    """Test that we can create tables"""
    tmpfilename = tempfile.NamedTemporaryFile(mode="w")
    db_name = tmpfilename.name
    db = DataBase(db_name)
    InitTaskTables(db, is_drop=True)
    tmpfilename.close()
