"""Persistence layer"""
import sqlite3


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
        schema_str = ", ".join(schema)
        self._execute(
            f"""CREATE TABLE if not exists {table_name} (
                {schema_str}
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
        self,
        table_name: str,
        colnames: list[str] = None,
        filter="",
        order="",
        add_index: bool = False,
        limit: int = None,
    ):
        if colnames:
            real_colnames = colnames
            colnames = ",".join(colnames)
        else:
            colnames = "*"
            real_colnames = self._get_colnames(table_name=table_name)

        if add_index and order:
            colnames = f"row_number() over (order by {order}) as idx, {colnames}"
            real_colnames = ("idx", *real_colnames)

        query = f"""select {colnames} from {table_name}"""
        if filter:
            query += f" where {filter} "
        if order:
            query += f" order by {order} "
        if limit:
            query += f" limit {limit}"
        res = self._execute(query)
        return res.fetchall(), real_colnames

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
        query = f"""update {table_name} set {','.join(values)}"""
        if filter:
            query += f"where {filter}"
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
