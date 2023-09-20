"""Main module with tasks logic"""
from datetime import datetime


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
        ...

    def create_task(self, name):
        ...
        # db.create task

    def edit_task(self, task_number):
        ...
        # db.edit

    def remove_task(self, task_number):
        ...

    def show_tasks(self):
        ...
