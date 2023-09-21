"""Main module with tasks logic"""
from datetime import datetime
from whatsup.db import DataBase

db = DataBase("current_tasks")


class Task:
    priority: int
    date_inserted: datetime
    deadline: datetime
    name: str
    description: str


class Plan:
    group: str
    ...


class Actions:
    def __init__(self):
        self.init_task_table()

    def init_task_table(self):
        db.drop_table("current_tasks")
        schema = [
            "task_number integer primary key AUTOINCREMENT not null",
            # it's not autoincrement
            "priority integer",
            "date_inserted timestamp",
            "deadline timestamp",
            "name varchar",
            "description varchar",
        ]
        self.colnames = [col_ddl.split(" ")[0] for col_ddl in schema]
        db.create_table(
            "current_tasks",
            schema,
        )

    def create_task(self, name):
        db.add_record("current_tasks", ["name"], [name])

    def done_task(self):
        ...

    def edit_task(self, task_number, value):
        db.update_record(
            "current_tasks", value=value, filter=f"task_number = {task_number}"
        )

    def remove_task(self, task_number):
        db.delete_record("current_tasks", filter=f"task_number = {task_number}")

    def show_tasks(self):
        res = db.fetch_records("current_tasks")
        return res


if __name__ == "__main__":
    action = Actions()
    action.create_task("task 1")
    action.create_task("task 2")
    action.edit_task("2", {"name": "task2 edited"})
    print(action.show_tasks())
    action.remove_task(1)
    action.create_task("task 3")
    print(action.show_tasks())
