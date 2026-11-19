import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "countries.db")


class Database:
    def __init__(self, db_file=DB_PATH):
        self.db_file = db_file
        self.create_table()
        self.create_users_table()

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
                "area INTEGER NOT NULL,"
                "user_id INTEGER)"
            )

    def create_country(self, common_name, official_name, population, html_flag_code, area, user_id=None):
        c = self._connect()
        try:
            with c:
                cur = c.execute(
                    "INSERT INTO countries (common_name, official_name, population, html_flag_code, area, user_id) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (common_name, official_name, population, html_flag_code, area, user_id),
                )
                new_id = cur.lastrowid
        finally:
            c.close()
        return self.get_country(new_id, user_id)

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

    def get_all_countries(self, user_id=None):
        c = self._connect()
        try:
            rows = c.execute("SELECT * FROM countries WHERE user_id IS ? ORDER BY id", (user_id,)).fetchall()
            return [dict(r) for r in rows]

        finally:
            c.close()

    def get_country(self, id, user_id=None):
        c = self._connect()
        try:
            row = c.execute("SELECT * FROM countries WHERE id = ? AND user_id = ?", (id, user_id)).fetchone()
            return dict(row) if row else None
        finally:
            c.close()

    def update_country(self, id, common_name, official_name, population, html_flag_code, area, user_id=None):
        c = self._connect()
        try:
            with c:
                cur = c.execute(
                    "UPDATE countries SET common_name = ?, official_name = ?, population = ?, "
                    "html_flag_code = ?, area = ? WHERE id = ? AND user_id = ?",
                    (common_name, official_name, population, html_flag_code, area, id, user_id),
                )
                updated = cur.rowcount > 0
        finally:
            c.close()
        return self.get_country(id, user_id) if updated else None

    def delete_country(self, id, user_id=None):
        c = self._connect()
        try:
            with c:
                cur = c.execute("DELETE FROM countries WHERE id = ? AND user_id = ?", (id,user_id))
                return cur.rowcount > 0
        finally:
            c.close()


    def create_users_table(self):
        with self._connect() as c:
            c.execute(
                "CREATE TABLE IF NOT EXISTS users("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "first_name TEXT NOT NULL,"
                "last_name TEXT NOT NULL,"
                "email TEXT NOT NULL UNIQUE COLLATE NOCASE,"
                "password_hash TEXT NOT NULL)"
                )

    def create_user(self, first, last, email, pw_hash):
        c = self._connect()
        try:
            with c:
                cur = c.execute(
                    "INSERT INTO users(first_name, last_name, email, password_hash) "
                    "VALUES(?,?,?,?)",
                    (first, last, email, pw_hash)
                    )
                new_id = cur.lastrowid
            c.close()
        except sqlite3.IntegrityError:
            return None
        return self.get_user(new_id)
    
    def get_user(self, id):
        c = self._connect()
        try:
            row = c.execute(
                "SELECT id, first_name, last_name, email FROM users WHERE id = ?",
                (id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            c.close()

    def get_user_by_email(self, email):
        c = self._connect()
        try:
            row = c.execute(
                "SELECT * FROM users WHERE email=?",
                (email,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            c.close()
