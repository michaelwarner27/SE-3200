import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "countries.db")


class Database:
    def __init__(self, db_file=DB_PATH):
        self.db_file = db_file
        self.create_table()

    def _connect(self):
        connection = sqlite3.connect(self.db_file)
        connection.row_factory = sqlite3.Row
        return connection

    def create_table(self):
        with self._connect() as c:
            c.execute(
                "CREATE TABLE IF NOT EXISTS countries("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "common_name TEXT NOT NULL,"
                "official_name TEXT NOT NULL,"
                "population INTEGER NOT NULL,"
                "html_flag_code TEXT NOT NULL,"
                "area INTEGER NOT NULL)"
            )

    def create_country(self, common_name, official_name, population, html_flag_code, area):
        c = self._connect()
        try:
            with c:
                cur = c.execute(
                    "INSERT INTO countries (common_name, official_name, population, html_flag_code, area) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (common_name, official_name, population, html_flag_code, area),
                )
                new_id = cur.lastrowid
        finally:
            c.close()
        return self.get_country(new_id)

    def create_countries(self, countries_data: list[tuple]):
        c = self._connect()
        try:
            with c:
                c.executemany(
                    "INSERT INTO countries (common_name, official_name, population, html_flag_code, area) "
                    "VALUES (?, ?, ?, ?, ?)",
                    countries_data,
                )
        finally:
            c.close()

    def get_all_countries(self):
        c = self._connect()
        try:
            return [dict(r) for r in c.execute("SELECT * FROM countries").fetchall()]
        finally:
            c.close()

    def get_country(self, id):
        c = self._connect()
        try:
            row = c.execute("SELECT * FROM countries WHERE id = ?", (id,)).fetchone()
            return dict(row) if row else None
        finally:
            c.close()

    def update_country(self, id, common_name, official_name, population, html_flag_code, area):
        c = self._connect()
        try:
            with c:
                cur = c.execute(
                    "UPDATE countries SET common_name = ?, official_name = ?, population = ?, "
                    "html_flag_code = ?, area = ? WHERE id = ?",
                    (common_name, official_name, population, html_flag_code, area, id),
                )
                updated = cur.rowcount > 0
        finally:
            c.close()
        return self.get_country(id) if updated else None

    def delete_country(self, id):
        c = self._connect()
        try:
            with c:
                cur = c.execute("DELETE FROM countries WHERE id = ?", (id,))
                return cur.rowcount > 0
        finally:
            c.close()
