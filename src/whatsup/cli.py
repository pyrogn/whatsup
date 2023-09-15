import typer


app = typer.Typer()
quick_app = typer.Typer()


@quick_app.callback(invoke_without_command=True)
@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    app()
    # quick_app()
