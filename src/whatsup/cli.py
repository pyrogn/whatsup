import typer
from whatsup.tasks import Actions, InitDB


app = typer.Typer()
quick_app = typer.Typer()


@quick_app.callback(invoke_without_command=True)
@app.command()
def show():
    action = Actions()
    print("\n".join(action.show_tasks()))


@app.command()
def add(name: str, priority: int = 1, deadline: int = 24):
    action = Actions()
    action.create_task(name=name, priority=priority, deadline=deadline)


@app.command()
def done(task_num: int):
    action = Actions()
    action.done_task(task_num)


@app.command()
def arc():
    action = Actions()
    print("\n".join(action.show_archived_tasks()))


@app.command()
def clean():
    InitDB(is_drop=True).archived_tasks()
    InitDB(is_drop=True).active_tasks()


if __name__ == "__main__":
    app()
    # quick_app()
