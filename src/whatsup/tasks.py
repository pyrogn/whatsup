"""Main module with tasks logic"""
from datetime import datetime, timedelta
from dataclasses import dataclass

from whatsup.db import DataBase

db = DataBase("whatsup.db")  # change name after


@dataclass
class Task:
    idx: int
    name: str
    deadline: str
    priority: int = 0

    @property
    def is_expired(self):
        return datetime.now() > datetime.strptime(self.deadline, "%Y-%m-%d %H:%M:%S")

    def __str__(self):
        my_hour = (
            datetime.strptime(self.deadline, "%Y-%m-%d %H:%M:%S") - datetime.now()
        ).seconds / 3600
        return (
            f"{self.idx}. {self.name}. priority={self.priority} "
            f"deadline={self.deadline} hour={my_hour:.1f}"
        )


@dataclass
class ArcTask:
    idx: int
    name: str
    reason: str
    ts_archived: str
    deadline: str
    priority: int = 1

    def __str__(self):
        return f"{self.idx}. {self.name}. reason={self.reason} deadline={self.deadline}"


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
        )
        return res, colnames

    def _make_archived_task_list(self, limit):
        res, colnames = db.fetch_records(
            "archived_tasks", order="ts_archived desc", add_index=True, limit=limit
        )
        return res, colnames

    def init_task_table(self):
        InitDB().active_tasks()
        InitDB().archived_tasks()

    def create_task(self, **values):
        # make a task constructor?
        values["deadline"] = (
            datetime.now() + timedelta(hours=values.get("deadline", 24))
        ).strftime("%Y-%m-%d %H:%M:%S")
        db.add_record("current_tasks", list(values.keys()), list(values.values()))

    def done_task(self, task_number: int) -> None:
        task_id = self.task_num_to_id(task_number)
        res, columns = db.fetch_records(
            "current_tasks",
            ["name", "deadline"],
            filter=f"id = {task_id}",
        )
        row = self.select_df(res, columns, ["name", "deadline"])[0]
        row["reason"] = "done"
        db.add_record(
            "archived_tasks",
            list(row.keys()),
            list(row.values()),
        )

        db.delete_record("current_tasks", filter=f"id = {task_id}")

    def task_num_to_id(self, task_num: int) -> int:
        """Get mapping task num to id (pk).
        Another option: add idx and filter directly on this column
            without extra read"""
        df, columns = db.fetch_records(
            "current_tasks",
            colnames=["id"],
            order="priority desc, date_inserted",
            add_index=True,
        )
        self.map_id_to_num = {int(idx): int(num) for idx, num in df}
        return self.map_id_to_num[int(task_num)]

    def edit_task(self, task_number: int, value: dict) -> None:
        task_id = self.task_num_to_id(task_number)
        db.update_record("current_tasks", value=value, filter=f"id = {task_id}")

    def remove_task(self, task_number: int) -> None:
        task_id = self.task_num_to_id(task_number)
        res, columns = db.fetch_records(
            "current_tasks",
            ["name", "deadline"],
            filter=f"id = {task_id}",
        )
        row = self.select_df(res, columns, ["name", "deadline"])[0]
        row["reason"] = "deleted"
        db.add_record(
            "archived_tasks",
            list(row.keys()),
            list(row.values()),
        )

        db.delete_record("current_tasks", filter=f"id = {task_id}")

    @staticmethod
    def df_to_str(df: list[dict], task_type) -> str:
        vals = df
        list_str = []

        for row in vals:
            list_str.append(str(task_type(**row)))
        return "\n".join(list_str)

    @staticmethod
    def select_df(
        df: list[tuple], columns: list[str], select_order: list[str]
    ) -> list[dict]:
        idx_cols = []
        for col in select_order:
            assert col in columns, f"{col} not in {columns}"
            idx_cols.append(columns.index(col))
        new_df = []
        for row in df:
            new_df.append(dict(zip(select_order, [row[idx] for idx in idx_cols])))
        return new_df

    def show_tasks(self) -> str:
        tasks_df, colnames = self._make_task_list()
        tasks_df = self.select_df(
            tasks_df, colnames, ["idx", "name", "priority", "deadline"]
        )
        return self.df_to_str(tasks_df, task_type=Task)

    def show_archived_tasks(self, limit: str = 10) -> str:
        tasks_df, colnames = self._make_archived_task_list(limit=limit)
        tasks_df = self.select_df(
            tasks_df,
            colnames,
            # add priority
            ["idx", "name", "deadline", "ts_archived", "reason"],
        )
        return self.df_to_str(tasks_df, task_type=ArcTask)


if __name__ == "__main__":
    action = Actions()
    action.create_task(name="task 1", priority=3)
    action.create_task(
        name="task 2",
    )
    # print(action._make_task_list())
    print(action.show_tasks())
    action.edit_task("2", {"name": "task2 edited"})
    print(action.show_tasks())
    action.done_task(1)
    action.remove_task(1)
    print()
    print(action.show_tasks())
    res, colnames = db.fetch_records("archived_tasks")
    print()
    print(res)
    # print(action.show_tasks())
    # action.remove_task(1)
    # action.create_task("task 3")
    # print(action.show_tasks())
