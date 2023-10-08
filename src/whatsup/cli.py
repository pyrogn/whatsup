"""CLI logic"""
import typer
from whatsup.tasks import TaskAction, InitTaskTables, db
from typing_extensions import Annotated


app = typer.Typer()
quick_app = typer.Typer()

action = TaskAction(db)


@quick_app.callback(invoke_without_command=True)
@app.command()
def show():
    """Show all active tasks"""
    print(action.show_tasks())


@app.command()
def add(
    name: str,
    priority: Annotated[int, typer.Option("--priority", "-p")] = 1,
    deadline: int = 24,
):
    """Add a new task"""
    action.create_task(name=name, priority=priority, deadline=deadline)


@app.command()
def done(task_num: int):
    """Mark a task as done"""
    action.done_task(task_num)


@app.command()
def rm(task_num: int):
    """Remove a task"""
    action.remove_task(int(task_num))


@app.command()
def arc():
    """Show archived tasks"""
    print(action.show_archived_tasks())


@app.command()
def upd(task_num, attr, value):
    """Update info about a task"""
    raise NotImplementedError


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
