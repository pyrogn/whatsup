"""Persistence layer"""
import sqlite3

conn = sqlite3.connect("current_tasks")  # make it constant and maybe somewhere global


class DataBase:
    def __init__(self, schema_name):
        self.schema_name = schema_name
        self.conn = sqlite3.connect(self.schema_name)

    def create_table(self, table_name=None, schema=None):
        with self.conn as c:
            c.execute(
                f"""CREATE TABLE if not exists {table_name} (
                                        {", ".join(schema)}
                                    )""",
            )

    def fetch_records(self, table_name=None, filter=None):
        with self.conn as c:
            res = c.execute(f"""select * from {table_name}""")
            return res.fetchall()

    def add_record(self, table_name, columns, values):
        with self.conn as c:
            data = [(i,) for i in values]
            c.executemany(
                f"insert into {table_name} ({','.join(columns)}) values (?)", data
            )

    def delete_record(self, table_name, filter: str):
        with self.conn as c:
            c.execute(f"delete from {table_name} where {filter}")

    def update_record(
        self,
        table_name,
        value,
        filter=None,
    ):
        with self.conn as c:
            values = [f"{i} = {j}" for i, j in value]
            c.execute(
                f"""update {table_name} set {','.join(values)}
                {"where filter" if filter else ''}"""
            )

    def truncate_table(self, table_name):
        with self.conn as c:
            c.execute(f"delete from {table_name}")


if __name__ == "__main__":
    db = DataBase("current_tasks")
    db.truncate_table("asdf2")
    db.create_table("asdf2", ["i integer"])
    db.add_record("asdf2", ["i"], [1, 2, 3, -98])
    print(db.fetch_records("asdf2"))
