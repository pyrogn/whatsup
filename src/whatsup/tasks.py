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
    priority: int = 1

    @property
    def is_expired(self):
        return datetime.now() > datetime.strptime(self.deadline, "%Y-%m-%d %H:%M:%S")

    @property
    def hours(self):
        hours_left = (
            datetime.strptime(self.deadline, "%Y-%m-%d %H:%M:%S") - datetime.now()
        ).total_seconds() / 3600
        return round(hours_left, 1)


@dataclass
class ArcTask:
    idx: int
    name: str
    reason: str
    ts_archived: str
    deadline: str
    priority: int = 1


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
        header = ["idx", "name", "priority", "reason", "ts_archived", "deadline"]
        return self._present_tasks_general(header)

    def _present_tasks_general(self, header):
        if not self.tasks:
            return "No tasks"
        max_lengths = self._find_max_len_task_attr(self.tasks, header)
        output = [
            "|".join([f"{i:<{max_lengths[i]}}" for i in header]),
            "+".join(["-" * val for val in max_lengths.values()]),
        ]
        for task in self.tasks:
            st = "|".join(
                [
                    f"{getattr(task, attr) or '':<{max_lengths[attr]}}"
                    for attr in header
                ]
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
            "priority integer",
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

    def _make_active_task_list(self):
        res = self.db.fetch_records(
            "current_tasks",
            colnames=["name", "priority", "deadline"],
            order="priority desc, date_inserted",
            add_index=True,
        )
        return res

    def _make_archived_task_list(self, limit):
        res = self.db.fetch_records(
            "archived_tasks",
            colnames=["name", "deadline", "ts_archived", "priority", "reason"],
            order="ts_archived desc",
            add_index=True,
            limit=limit,
        )
        return res

    def init_task_table(self):
        InitTaskTables(self.db).active_tasks()
        InitTaskTables(self.db).archived_tasks()

    def create_task(self, **values):
        # make a task constructor?
        values["deadline"] = (
            datetime.now() + timedelta(hours=values.get("deadline", 24))
        ).strftime("%Y-%m-%d %H:%M:%S")
        self.db.add_record("current_tasks", values)

    def done_task(self, task_number: int) -> None:
        self._move_active_task_to_arc(task_number, "done")

    def task_num_to_id(self, task_num: int) -> int:
        """Get mapping task num to id (pk).
        Another option: add idx and filter directly on this column
            without extra read"""
        df = self.db.fetch_records(
            "current_tasks",
            colnames=["id"],
            order="priority desc, date_inserted",
            add_index=True,
        )
        self.map_id_to_num = {row["idx"]: row["id"] for row in df}
        return self.map_id_to_num[int(task_num)]

    def edit_task(self, task_number: int, value: dict) -> None:
        task_id = self.task_num_to_id(task_number)
        self.db.update_record("current_tasks", value=value, filter=f"id = {task_id}")

    def remove_task(self, task_number: int) -> None:
        self._move_active_task_to_arc(task_number, "rm")

    def _move_active_task_to_arc(
        self, task_number: int, reason: Literal["rm", "done"]
    ):
        task_id = self.task_num_to_id(task_number)
        row = self.db.fetch_records(
            "current_tasks",
            ["name", "deadline", "priority"],
            filter=f"id = {task_id}",
        )[0]
        map_reason = {"rm": "deleted", "done": "done"}
        row["reason"] = map_reason[reason]
        self.db.add_record("archived_tasks", row)

        self.db.delete_record("current_tasks", filter=f"id = {task_id}")

    @staticmethod
    def df_to_str(df: list[dict], task_type: Literal["active", "arc"]) -> str:
        task_class_map = {"active": ActiveTask, "arc": ArcTask}
        task_collection = [task_class_map[task_type](**row) for row in df]
        return TasksPrettyTable(task_type, task_collection).present_tasks()

    def show_tasks(self) -> str:
        tasks_df = self._make_active_task_list()
        return self.df_to_str(tasks_df, task_type="active")

    def show_archived_tasks(self, limit: int = 10) -> str:
        tasks_df = self._make_archived_task_list(limit=limit)
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
    # res, colnames = db.fetch_records("archived_tasks")
    # print()
    # print(res)
    # print(action.show_tasks())
    # action.remove_task(1)
    # action.create_task("task 3")
    # print(action.show_tasks())
