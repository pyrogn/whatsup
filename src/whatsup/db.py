"""Persistence layer"""
import sqlite3

conn = sqlite3.connect("current_tasks")  # make it constant and maybe somewhere global


class DataBase:
    def __init__(self, schema_name):
        self.schema_name = schema_name
        self.conn = sqlite3.connect(self.schema_name)

    def __del__(self):
        self.conn.close()

    def _execute(self, query, data=""):
        with self.conn as c:
            c.execute(query, data)

    def _executemany(self, query, data=""):
        with self.conn as c:
            c.executemany(query, data)

    def create_table(self, table_name=None, schema: list[str] = None):
        self._execute(
            f"""CREATE TABLE if not exists {table_name} (
                    {", ".join(schema)}
                )""",
        )

    def fetch_records(self, table_name: str, colnames="*", filter=""):
        with self.conn as c:
            filter = f"where {filter}" if filter else ""
            if colnames != "*":
                colnames = ",".join(colnames)
            res = c.execute(f"""select {colnames} from {table_name} {filter}""")
            return res.fetchall()  # add colnames probably

    def add_record(self, table_name, columns, values):
        with self.conn as c:
            data = [(i,) for i in values]
            c.executemany(
                f"insert into {table_name} ({','.join(columns)}) values (?)", data
            )

    def delete_record(self, table_name, filter: str):
        self._execute(f"delete from {table_name} where {filter}")

    def update_record(
        self,
        table_name,
        value: dict,
        filter="",
    ):
        with self.conn as c:
            values = [f"{i} = {j!r}" for i, j in value.items()]
            filter = f"where {filter}" if filter else ""
            query = f"""update {table_name} set {','.join(values)}
                {filter}"""
            print(query)
            c.execute(query)

    def truncate_table(self, table_name):
        self._execute(f"delete from {table_name}")

    def drop_table(self, table_name):
        self._execute(f"drop table if exists {table_name}")

    def take_max(self, table_name):
        ...


if __name__ == "__main__":
    db = DataBase("current_tasks")
    db.create_table("asdf2", ["i integer"])
    db.truncate_table("asdf2")
    db.add_record("asdf2", ["i"], [1, 2, 3, -98])
    print(db.fetch_records("asdf2"))
    print(type(db.fetch_records("asdf2")[0]))
    db.update_record("asdf2", {"i": 8}, filter="i=-98")
    print(db.fetch_records("asdf2"))
    db.delete_record("asdf2", filter="i=1")
    # db.drop_table("asdf2")
    print(db.fetch_records("asdf2", colnames=["i"]))
