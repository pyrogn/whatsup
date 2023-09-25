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
    def __init__(self, is_drop=False):
        self.is_drop = is_drop

    def archived_tasks(self):
        if self.is_drop:
            db.drop_table("archived_tasks")
        schema = [
            "id integer primary key autoincrement not null",
            "ts_archived timestamp default current_timestamp",
            "reason varchar",
            "name varchar",
            "description varchar",
            "deadline timestamp",
        ]
        db.create_table("archived_tasks", schema=schema)

    def active_tasks(self):
        if self.is_drop:
            db.drop_table("current_tasks")
        schema = [
            "id integer primary key autoincrement not null",
            "priority integer default 1",
            "date_inserted timestamp default current_timestamp",
            "deadline timestamp",
            "name varchar",
            "description varchar",
        ]
        db.create_table(
            "current_tasks",
            schema,
        )


class Actions:
    def __init__(self):
        self.init_task_table()
        self.map_id_to_num = {}

    def _make_task_list(self):
        res, colnames = db.fetch_records("current_tasks")
        df = pd.DataFrame(res, columns=colnames)  # consider using only sqllite3
        df = df.sort_values(["priority", "date_inserted"], ascending=[False, True])
        df = df.reset_index(drop=True)
        df = df.reset_index(names=["task_num"])
        df["task_num"] = df["task_num"] + 1
        return df

    def init_task_table(self):
        InitDB().active_tasks()
        InitDB().archived_tasks()

    def create_task(self, **values):
        db.add_record("current_tasks", list(values.keys()), list(values.values()))

    def add_task_num(self):
        res, columns = db.query(
            """select *, row_number() over (order by priority desc, deadline) task_num
        from current_tasks
        order by task_num"""
        )
        return res, columns

    def done_task(self, task_number: int):
        # res = db.fetch_records("current_tasks", filter=f"task_number = {task_number}")
        task_id = self.task_num_to_id(task_number)
        res, columns = db.fetch_records(
            "current_tasks",
            ["name", "description", "deadline"],
            filter=f"id = {task_id}",
        )
        res_df = pd.DataFrame(res, columns=columns)
        db.delete_record("current_tasks", filter=f"id = {task_id}")
        cols_insert = ["name", "description", "deadline"]
        db.add_record(
            "archived_tasks",
            ["reason"] + cols_insert,
            ["done", *res_df[cols_insert].values[0]],
        )

    def task_num_to_id(self, task_num):
        """Get mapping task num to id (pk)"""
        res, columns = self.add_task_num()
        res_df = pd.DataFrame(res, columns=columns)
        self.map_id_to_num = res_df.set_index("task_num").to_dict()["id"]
        return self.map_id_to_num[int(task_num)]

    def edit_task(self, task_number, value):
        task_id = self.task_num_to_id(task_number)
        db.update_record("current_tasks", value=value, filter=f"id = {task_id}")

    def remove_task(self, task_number):
        task_id = self.task_num_to_id(task_number)
        res, columns = db.fetch_records(
            "current_tasks",
            ["name", "description", "deadline"],
            filter=f"id = {task_id}",
        )
        res_df = pd.DataFrame(res, columns=columns)
        db.delete_record("current_tasks", filter=f"id = {task_id}")
        cols_insert = ["name", "description", "deadline"]
        db.add_record(
            "archived_tasks",
            ["reason"] + cols_insert,
            ["deleted", *res_df[cols_insert].values[0]],
        )

    @staticmethod
    def df_to_str(df, show_cols=None):
        show_cols = show_cols or []
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
        tasks_df = self._make_task_list()
        tasks_df = tasks_df[["task_num", "name", "description", "priority"]]
        return self.df_to_str(tasks_df, show_cols=["priority"])


if __name__ == "__main__":
    action = Actions()
    action.create_task(name="task 1", priority=3, description="Descr1")
    action.create_task(name="task 2", description="Descr2")
    print(action.add_task_num())
    # print(action._make_task_list())
    print("\n".join(action.show_tasks()))
    action.edit_task("2", {"name": "task2 edited"})
    print("\n".join(action.show_tasks()))
    action.done_task(1)
    action.remove_task(1)
    print()
    print("\n".join(action.show_tasks()))
    res, colnames = db.fetch_records("archived_tasks")
    df = pd.DataFrame(res, columns=colnames)  # consider using only sqllite3
    print()
    print(res)
    # print(action.show_tasks())
    # action.remove_task(1)
    # action.create_task("task 3")
    # print(action.show_tasks())
