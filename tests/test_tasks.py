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
        action.create_task(name=f"test_task{i}")
    db = DataBase(db_name)
    res, columns = db.fetch_records("current_tasks")
    assert len(res) == n_tasks
    db.truncate_table("current_tasks")
    res, columns = db.fetch_records("current_tasks")
    assert not len(res)


def test_edit_task():
    pass


def test_done_task(create_db):
    db_name, action = create_db
    n_tasks = 20
    for i in range(n_tasks):
        action.create_task(name=f"test_task{i}")
    db = DataBase(db_name)
    res, columns = db.fetch_records("current_tasks")
    assert len(res) == n_tasks
    for _ in range(n_tasks):
        action.done_task(1)
    res, columns = db.fetch_records("current_tasks")
    assert not len(res)


def test_rm_task():
    pass


def test_arc_task():
    pass
