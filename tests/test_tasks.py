"""Tests for managing tasks"""
from whatsup.tasks import TaskAction, InitTaskTables
from whatsup.db import DataBase
import tempfile
import pytest


@pytest.fixture(scope="function")
def create_db():
    tmpfilename = tempfile.NamedTemporaryFile(mode="w")
    db_name = tmpfilename.name
    db = DataBase(db_name)
    InitTaskTables(db, is_drop=True)
    action = TaskAction(db)
    yield db_name, action
    tmpfilename.close()


def test_create_task(create_db):
    db_name, action = create_db
    n_tasks = 20
    for i in range(n_tasks):
        action.add_task(name=f"test_task{i}")
    db = DataBase(db_name)
    res = db.fetch_records("active_tasks")
    assert len(res) == n_tasks
    db.truncate_table("active_tasks")
    res = db.fetch_records("active_tasks")
    assert not len(res)


def test_edit_task(create_db):
    db_name, action = create_db
    db = DataBase(db_name)
    initial_info = {"name": "test_task1", "priority": 3}
    action.add_task(**initial_info)

    def get_subset_dict(bigdict, keys):
        return {k: bigdict[k] for k in bigdict.keys() if k in keys}

    assert (
        get_subset_dict(db.fetch_records("active_tasks")[0], {"name", "priority"})
        == initial_info
    )

    new_info = {"name": "test_task2", "priority": 2}
    action.edit_task(1, new_info)
    assert (
        get_subset_dict(db.fetch_records("active_tasks")[0], {"name", "priority"})
        == new_info
    )


def test_done_task(create_db):
    db_name, action = create_db
    n_tasks = 20
    for i in range(n_tasks):
        action.add_task(name=f"test_task{i}")
    db = DataBase(db_name)
    res = db.fetch_records("active_tasks")
    assert len(res) == n_tasks
    for _ in range(n_tasks):
        action.done_task(1)
    res = db.fetch_records("active_tasks")
    assert not len(res)
    assert all(rec["reason"] == "done" for rec in db.fetch_records("archived_tasks"))


def test_rm_task(create_db):
    db_name, action = create_db
    n_tasks = 20
    for i in range(n_tasks):
        action.add_task(name=f"test_task{i}")
    db = DataBase(db_name)
    res = db.fetch_records("active_tasks")
    assert len(res) == n_tasks
    for _ in range(n_tasks):
        action.rm_task(1)
    res = db.fetch_records("active_tasks")
    assert not len(res)
    assert all(
        rec["reason"] == "deleted" for rec in db.fetch_records("archived_tasks")
    )


def test_arc_task():
    """Might want to test archived tasks separately"""
    ...
