"""Main module with tasks logic"""
from datetime import datetime, timedelta
from dataclasses import dataclass

import pandas as pd

from whatsup.db import DataBase

db = DataBase("current_tasks")


@dataclass
class Task:
    name: str
    description: str
    date_inserted: datetime
    priority: int = 0
    deadline: int = 24

    @property
    def is_expired(self):
        return datetime.now() > self.date_inserted + timedelta(hours=self.deadline)

    def __gt__(self, other):
        return (self.priority, self.deadline) > (other.priority, other.deadline)


class InitDB:
    def __init__(self):
        ...

    def archived_tasks(self):
        schema = [
            "ts_archived timestamp default current_timestamp",
            "reason varchar",
            "name varchar",
            "description varchar",
        ]
        db.create_table("archived_tasks", schema=schema)

    def active_tasks(self):
        db.drop_table("current_tasks")
        schema = [
            "priority integer default 1",
            "date_inserted timestamp default current_timestamp",
            "deadline timestamp",
            "name varchar",
            "description varchar",
        ]
        self.colnames = [col_ddl.split(" ")[0] for col_ddl in schema]
        db.create_table(
            "current_tasks",
            schema,
        )


class Actions:
    def __init__(self):
        self.init_task_table()

    def _make_task_list(self):
        res, colnames = db.fetch_records("current_tasks")
        df = pd.DataFrame(res, columns=colnames)  # consider using only sqllite3
        df = df.sort_values(["priority", "date_inserted"], ascending=[False, True])
        df = df.reset_index(names=["task_num"])
        df["task_num"] = df["task_num"] + 1
        return df

    def init_task_table(self):
        InitDB().active_tasks()

    def create_task(self, **values):
        db.add_record("current_tasks", list(values.keys()), list(values.values()))

    def done_task(self, task_number: int):
        # res = db.fetch_records("current_tasks", filter=f"task_number = {task_number}")
        db.delete_record("current_tasks", filter=f"task_number = {task_number}")
        db.add_record(
            "archived_tasks",
        )  # make it work

    def edit_task(self, task_number, value):
        db.update_record(
            "current_tasks", value=value, filter=f"task_number = {task_number}"
        )

    def remove_task(self, task_number):
        db.delete_record("current_tasks", filter=f"task_number = {task_number}")

    @staticmethod
    def df_to_str(df, show_cols):
        cols = df.columns
        vals = df.values
        list_str = []

        def str_col(col, val):
            if col not in show_cols:
                return str(val)
            return f"{col}: {val}"

        for row in vals:
            list_str.append(". ".join(str_col(col, val) for col, val in zip(cols, row)))
        return list_str

    def show_tasks(self):
        # res, colnames = db.fetch_records("current_tasks")
        tasks_df = self._make_task_list()
        tasks_df = tasks_df[["task_num", "name", "description", "priority"]]
        return self.df_to_str(tasks_df, show_cols=["priority"])


if __name__ == "__main__":
    action = Actions()
    action.create_task(name="task 1", priority=3, description="Descr1")
    action.create_task(name="task 2", description="Descr2")
    # print(action._make_task_list())
    print("\n".join(action.show_tasks()))
    # action.edit_task("2", {"name": "task2 edited"})
    # print(action.show_tasks())
    # action.remove_task(1)
    # action.create_task("task 3")
    # print(action.show_tasks())
