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
            res = c.execute(query, data)
            return res

    def _executemany(self, query, data=""):
        with self.conn as c:
            c.executemany(query, data)

    def create_table(self, table_name=None, schema: list[str] = None):
        self._execute(
            f"""CREATE TABLE if not exists {table_name} (
                    {", ".join(schema)}
            )""",
        )

    def select(self, query):
        with self.conn as c:
            res = c.execute(query)
            real_colnames = self._get_colnames(query=query)
            return res.fetchall(), real_colnames

    def _get_colnames(self, table_name=None, query=None):
        with self.conn as c:
            table_name_query = f"select * from {table_name}"
            query = query or table_name_query
            real_colnames = next(zip(*c.execute(query).description))
            return real_colnames

    def fetch_records(
        self, table_name: str, colnames: list[str] = None, filter="", order=""
    ):
        filter = f"where {filter}" if filter else ""
        if colnames:
            real_colnames = colnames
            colnames = ",".join(colnames)
        else:
            colnames = "*"
            real_colnames = self._get_colnames(table_name=table_name)

        query = f"""select {colnames} from {table_name} {filter}"""
        if order:
            query += f" order by {order}"
        res = self._execute(query)
        return res.fetchall(), real_colnames  # add colnames probably

    def add_record(self, table_name, columns, values):
        query = (
            f"insert into {table_name} ({','.join(columns)}) "
            f"values ({', '.join(['?'] * len(values))})"
        )
        self._execute(query, values)

    def delete_record(self, table_name, filter: str):
        self._execute(f"delete from {table_name} where {filter}")

    def update_record(
        self,
        table_name,
        value: dict,
        filter="",
    ):
        values = [f"{i} = {j!r}" for i, j in value.items()]
        filter = f"where {filter}" if filter else ""
        query = f"""update {table_name} set {','.join(values)}
            {filter}"""
        self._execute(query)

    def truncate_table(self, table_name):
        self._execute(f"delete from {table_name}")

    def drop_table(self, table_name):
        self._execute(f"drop table if exists {table_name}")


if __name__ == "__main__":
    db = DataBase("current_tasks")
    db.create_table("asdf2", ["i integer"])
    db.truncate_table("asdf2")
    # db.add_record("asdf2", ["i"], [1, 2, 3, -98])
    # print(db.fetch_records("asdf2"))
    # db.update_record("asdf2", {"i": 8}, filter="i=-98")
    # print(db.fetch_records("asdf2"))
    # db.delete_record("asdf2", filter="i=1")
    # print(db.fetch_records("asdf2", colnames=["i"]))
