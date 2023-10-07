"""Main module with tasks logic"""
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Collection, Literal

from whatsup.db import DataBase

db = DataBase("whatsup.db")


@dataclass
class ActiveTask:
    idx: int
    name: str
    deadline: str
    priority: int = 0

    @property
    def is_expired(self):
        return datetime.now() > datetime.strptime(self.deadline, "%Y-%m-%d %H:%M:%S")

    @property
    def hours(self):
        hours_left = round(
            (
                datetime.strptime(self.deadline, "%Y-%m-%d %H:%M:%S") - datetime.now()
            ).total_seconds()
            / 3600,
            1,
        )
        return hours_left

    def __str__(self):
        return f"{self.idx:<2}|{self.name:<30}|{self.priority:<1}|{self.hours:.1f}"


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


@dataclass
class TasksPrettyTable:
    task_type: Literal["active", "arc"]
    tasks: Collection[ActiveTask | ArcTask]

    def present_tasks(self) -> str:
        if self.task_type == "active":
            str_output = self._present_current_tasks()
        elif self.task_type == "arc":
            str_output = self._present_arc_tasks()
        else:
            raise ValueError(f"{self.task_type} not in ['active', 'arc']")
        return str_output

    @staticmethod
    def _find_max_len_task_attr(
        collection: Collection[ActiveTask | ArcTask],
        attrs: list[str],
    ) -> dict[str, int]:
        max_lengths = {}
        for attr in attrs:
            max_len = max([len(str(getattr(task, attr))) for task in collection])
            max_lengths[attr] = max(max_len, len(attr))
        return max_lengths

    def _present_current_tasks(self) -> str:
        header = ["idx", "name", "priority", "hours"]
        return self._present_tasks_general(header)

    def _present_arc_tasks(self) -> str:
        header = ["idx", "name", "reason", "deadline"]
        return self._present_tasks_general(header)

    def _present_tasks_general(self, header):
        max_lengths = self._find_max_len_task_attr(self.tasks, header)
        output = [
            "|".join([f"{i:<{max_lengths[i]}}" for i in header]),
            "+".join(["-" * val for val in max_lengths.values()]),
        ]
        for task in self.tasks:
            st = "|".join(
                [f"{getattr(task, attr):<{max_lengths[attr]}}" for attr in header]
            )
            output.append(st)
        return "\n".join(output)


class InitTaskTables:
    """Initialize tables for current and archived tasks"""

    def __init__(self, db, is_drop=False):
        self.db = db
        self.is_drop = is_drop

    def archived_tasks(self):
        if self.is_drop:
            self.db.drop_table("archived_tasks")
        schema = [
            "id integer primary key autoincrement not null",
            "ts_archived timestamp default current_timestamp",
            "reason varchar",
            "name varchar",
            "deadline timestamp",
        ]
        self.db.create_table("archived_tasks", schema=schema)

    def active_tasks(self):
        if self.is_drop:
            self.db.drop_table("current_tasks")
        schema = [
            "id integer primary key autoincrement not null",
            "priority integer default 1",
            "date_inserted timestamp default current_timestamp",
            "deadline timestamp",
            "name varchar",
        ]
        self.db.create_table("current_tasks", schema)


class TaskAction:
    def __init__(self, db):
        self.db = db
        self.init_task_table()
        self.map_id_to_num = {}

    def _make_task_list(self):
        res, colnames = self.db.fetch_records(
            "current_tasks",
            order="priority desc, date_inserted",
            add_index=True,
        )
        return res, colnames

    def _make_archived_task_list(self, limit):
        res, colnames = self.db.fetch_records(
            "archived_tasks", order="ts_archived desc", add_index=True, limit=limit
        )
        return res, colnames

    def init_task_table(self):
        InitTaskTables(self.db).active_tasks()
        InitTaskTables(self.db).archived_tasks()

    def create_task(self, **values):
        # make a task constructor?
        values["deadline"] = (
            datetime.now() + timedelta(hours=values.get("deadline", 24))
        ).strftime("%Y-%m-%d %H:%M:%S")
        self.db.add_record("current_tasks", list(values.keys()), list(values.values()))

    def done_task(self, task_number: int) -> None:
        task_id = self.task_num_to_id(task_number)
        res, columns = self.db.fetch_records(
            "current_tasks",
            ["name", "deadline"],
            filter=f"id = {task_id}",
        )
        row = self.select_df(res, columns, ["name", "deadline"])[0]
        row["reason"] = "done"
        self.db.add_record(
            "archived_tasks",
            list(row.keys()),
            list(row.values()),
        )

        self.db.delete_record("current_tasks", filter=f"id = {task_id}")

    def task_num_to_id(self, task_num: int) -> int:
        """Get mapping task num to id (pk).
        Another option: add idx and filter directly on this column
            without extra read"""
        df, columns = self.db.fetch_records(
            "current_tasks",
            colnames=["id"],
            order="priority desc, date_inserted",
            add_index=True,
        )
        self.map_id_to_num = {int(idx): int(num) for idx, num in df}
        return self.map_id_to_num[int(task_num)]

    def edit_task(self, task_number: int, value: dict) -> None:
        task_id = self.task_num_to_id(task_number)
        self.db.update_record("current_tasks", value=value, filter=f"id = {task_id}")

    def remove_task(self, task_number: int) -> None:
        task_id = self.task_num_to_id(task_number)
        res, columns = self.db.fetch_records(
            "current_tasks",
            ["name", "deadline"],
            filter=f"id = {task_id}",
        )
        row = self.select_df(res, columns, ["name", "deadline"])[0]
        row["reason"] = "deleted"
        self.db.add_record(
            "archived_tasks",
            list(row.keys()),
            list(row.values()),
        )

        self.db.delete_record("current_tasks", filter=f"id = {task_id}")

    @staticmethod
    def df_to_str(df: list[dict], task_type: Literal["active", "arc"]) -> str:
        task_collection = []
        task_class_map = {"active": ActiveTask, "arc": ArcTask}
        for row in df:
            task_collection.append(task_class_map[task_type](**row))
        return TasksPrettyTable(task_type, task_collection).present_tasks()

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
        return self.df_to_str(tasks_df, task_type="active")

    def show_archived_tasks(self, limit: str = 10) -> str:
        tasks_df, colnames = self._make_archived_task_list(limit=limit)
        tasks_df = self.select_df(
            tasks_df,
            colnames,
            # add priority
            ["idx", "name", "deadline", "ts_archived", "reason"],
        )
        return self.df_to_str(tasks_df, task_type="arc")


if __name__ == "__main__":
    action = TaskAction(db)
    action.create_task(name="task 1", priority=3)
    action.create_task(
        name="task 2",
    )
    # print(action._make_task_list())
    print(action.show_tasks())
    action.edit_task(2, {"name": "task2 edited"})
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
