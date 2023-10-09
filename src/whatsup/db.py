"""Persistence layer"""
import sqlite3
from sqlite3 import Cursor


class DataBase:
    def __init__(self, schema_name):
        """schema_name - name of db file"""
        self.schema_name = schema_name
        self.conn = sqlite3.connect(self.schema_name)

    def __del__(self):
        self.conn.close()

    def _execute(
        self,
        query: str,
        data: list[str] | None = None,
    ) -> Cursor:
        with self.conn as c:
            if data:
                return c.execute(query, data)
            return c.execute(query)

    def _executemany(self, query, data=""):
        with self.conn as c:
            c.executemany(query, data)

    def create_table(self, table_name: str, schema: list[str]) -> None:
        """Create table with provided schema"""
        schema_str = ", ".join(schema)
        self._execute(
            f"""CREATE TABLE if not exists {table_name} (
                {schema_str}
            )""",
        )

    def select(self, query: str) -> list[dict]:
        """Run custom query"""
        res = self._execute(query)
        real_colnames = self._get_colnames(query=query)
        return [dict(zip(real_colnames, row)) for row in res.fetchall()]

    def _get_colnames(self, table_name: str = "", query: str = "") -> list[str]:
        """Get columns from the table or from query to the table"""
        with self.conn as c:
            table_name_query = f"select * from {table_name}"
            query = query or table_name_query
            real_colnames = next(zip(*c.execute(query).description))
            return real_colnames

    def fetch_records(
        self,
        table_name: str,
        colnames: list[str] | None = None,
        filter: str = "",
        order: str = "",
        add_index: bool = False,
        limit: int | None = None,
    ) -> list[dict]:
        """Form sql query and get a result"""
        if colnames:
            real_colnames = colnames
            colnames_query = ",".join(colnames)
        else:
            real_colnames = self._get_colnames(table_name=table_name)
            colnames_query = "*"

        if add_index and order:
            colnames_query = (
                f"row_number() over (order by {order}) as idx, {colnames_query}"
            )
            real_colnames.insert(0, "idx")

        query = f"""select {colnames_query} from {table_name}"""
        if filter:
            query += f" where {filter} "
        if order:
            query += f" order by {order} "
        if limit:
            query += f" limit {limit}"

        res = self._execute(query)
        return [dict(zip(real_colnames, row)) for row in res.fetchall()]

    def add_record(self, table_name: str, values: dict) -> None:
        """Add one record to a table"""
        query = (
            f"insert into {table_name} ({','.join(values)}) "
            f"values ({', '.join(['?'] * len(values.values()))})"
        )
        self._execute(query, list(values.values()))

    def delete_record(self, table_name: str, filter: str) -> None:
        self._execute(f"delete from {table_name} where {filter}")

    def update_record(
        self,
        table_name: str,
        value: dict,
        filter: str = "",
    ) -> None:
        """Update values in columns with optional filter"""
        values_query = ",".join([f"{i} = {j!r}" for i, j in value.items()])
        query = f"""update {table_name} set {values_query}"""
        if filter:
            query += f" where {filter} "
        self._execute(query)

    def truncate_table(self, table_name: str) -> None:
        self._execute(f"delete from {table_name}")

    def drop_table(self, table_name: str) -> None:
        self._execute(f"drop table if exists {table_name}")


if __name__ == "__main__":
    db = DataBase("whatsup.db")
    db.create_table("asdf2", ["i integer"])
    db.truncate_table("asdf2")
    db.add_record("asdf2", {"i": 9})
    print(db.fetch_records("asdf2"))
    db.update_record("asdf2", {"i": 8}, filter="i=9")
    print(db.fetch_records("asdf2"))
    db.delete_record("asdf2", filter="i=8")
    print(db.fetch_records("asdf2", colnames=["i"]))
