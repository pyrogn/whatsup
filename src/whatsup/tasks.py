"""Main module with tasks logic"""
from datetime import datetime, timedelta
from dataclasses import dataclass

from whatsup.db import DataBase

db = DataBase("current_tasks")


@dataclass
class Task:  # never used though
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
        res, colnames = db.fetch_records(
            "current_tasks",
            order="priority desc, date_inserted",
            add_index=True,
            add_hours=True,
        )
        return res, colnames

    def _make_archived_task_list(self):
        res, colnames = db.fetch_records(
            "archived_tasks", order="ts_archived desc", add_index=True
        )
        return res, colnames

    def init_task_table(self):
        InitDB().active_tasks()
        InitDB().archived_tasks()

    def create_task(self, **values):
        values["deadline"] = (
            datetime.now() + timedelta(hours=values.get("deadline", 24))
        ).strftime("%Y-%m-%d %H:%M:%S")
        db.add_record("current_tasks", list(values.keys()), list(values.values()))

    def add_task_num(self):
        res, columns = db.select(
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
            ["name", "deadline"],
            filter=f"id = {task_id}",
        )
        db.delete_record("current_tasks", filter=f"id = {task_id}")
        cols_insert = ["name", "deadline"]
        idx_list = []
        for idx, colname in enumerate(columns):
            if colname in cols_insert:
                idx_list.append(idx)
        db.add_record(
            "archived_tasks",
            ["reason"] + cols_insert,
            ["done", *[res[0][idx] for idx in idx_list]],
        )

    def task_num_to_id(self, task_num):
        """Get mapping task num to id (pk)"""
        df, columns = db.fetch_records(
            "current_tasks",
            colnames=["id"],
            order="priority desc, date_inserted",
            add_index=True,
        )
        self.map_id_to_num = {int(idx): int(num) for idx, num in df}
        return self.map_id_to_num[int(task_num)]

    def edit_task(self, task_number, value):
        task_id = self.task_num_to_id(task_number)
        db.update_record("current_tasks", value=value, filter=f"id = {task_id}")

    def remove_task(self, task_number):
        task_id = self.task_num_to_id(task_number)
        res, columns = db.fetch_records(
            "current_tasks",
            ["name", "deadline"],
            filter=f"id = {task_id}",
        )
        cols_insert = ["name", "deadline"]
        idx_list = []
        for idx, colname in enumerate(columns):
            if colname in cols_insert:
                idx_list.append(idx)
        db.delete_record("current_tasks", filter=f"id = {task_id}")
        db.add_record(
            "archived_tasks",
            ["reason"] + cols_insert,
            ["deleted", *[res[0][idx] for idx in idx_list]],
        )

    @staticmethod
    def df_to_str(df, colnames, show_cols=None):
        show_cols = show_cols or []
        cols = colnames
        vals = df
        list_str = []

        def str_col(col, val):
            if col not in show_cols:
                return str(val)
            return f"{col}: {val}"

        for row in vals:
            list_str.append(". ".join(str_col(col, val) for col, val in zip(cols, row)))
        return list_str

    def select_df(self, df, columns, select_order):
        idx_cols = []
        for col in select_order:
            idx_cols.append(columns.index(col))
        new_df = []
        for row in df:
            new_df.append([row[idx] for idx in idx_cols])
        return new_df, select_order

    def show_tasks(self):
        tasks_df, colnames = self._make_task_list()
        tasks_df, colnames = self.select_df(
            tasks_df, colnames, ["idx", "name", "priority", "deadline", "hour"]
        )
        return self.df_to_str(
            tasks_df, colnames, show_cols=["priority", "deadline", "hour"]
        )

    def show_archived_tasks(self):
        return self.df_to_str(*self._make_archived_task_list())


if __name__ == "__main__":
    action = Actions()
    action.create_task(name="task 1", priority=3)
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
    print()
    print(res)
    # print(action.show_tasks())
    # action.remove_task(1)
    # action.create_task("task 3")
    # print(action.show_tasks())
