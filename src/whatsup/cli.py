"""CLI logic"""
import sys

import typer
from whatsup.tasks import TaskAction, InitTaskTables, db
from typing_extensions import Annotated

# deadline doesn't work correctly for now
AVAILABLE_ATTRS_UPD = ["name", "deadline", "priority"]

app = typer.Typer()
quick_app = typer.Typer()

action = TaskAction(db)


@quick_app.callback(invoke_without_command=True)
@app.command()
def show():
    """Show all active tasks"""
    print(action.show_active_tasks())


@app.command()
def add(
    name: str,
    priority: Annotated[int, typer.Option("--priority", "-p")] = 1,
    deadline: int = 24,
):
    """Add a new task"""
    action.add_task(name=name, priority=priority, deadline=deadline)


@app.command()
def done(task_num: int):
    """Mark a task as done"""
    action.done_task(task_num)


@app.command()
def rm(task_num: int):
    """Remove a task"""
    action.rm_task(int(task_num))


@app.command()
def arc():
    """Show archived tasks"""
    print(action.show_archived_tasks())


@app.command()
def upd(task_num: int, attr: str, value: str):
    """Update info about a task

    Format: task_num attr value
    """
    if attr not in AVAILABLE_ATTRS_UPD:
        print(f"choose attr from {AVAILABLE_ATTRS_UPD}")
        sys.exit(1)
    action.edit_task(task_num, {attr: value})


@app.command()
def init():
    """Init db in stable place to be available globally"""
    raise NotImplementedError


@app.command()
def clean():
    """Clean DB with active and archived tasks"""
    init_db = InitTaskTables(db, is_drop=True)
    init_db.archived_tasks()
    init_db.active_tasks()


if __name__ == "__main__":
    app()
