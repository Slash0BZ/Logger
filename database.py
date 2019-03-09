import os
import sqlite3
import time
from flask import g


class CogCompLoggerDB:

    def __init__(self, db_loc=None):
        if db_loc is None:
            self.db_loc = "./logger.db"
        else:
            self.db_loc = db_loc

    def get_db(self):
        if 'db' not in g:
            g.db = sqlite3.connect(self.db_loc)
        return g.db

    def initialize_default_db(self):
        db = self.get_db()
        cursor = db.cursor()
        # Create a table for operation authentication
        cursor.execute("CREATE TABLE IF NOT EXISTS auth (name TEXT PRIMARY KEY, url TEXT, email TEXT)")
        # Create a table for counter storage
        cursor.execute("CREATE TABLE IF NOT EXISTS counter (name TEXT PRIMARY KEY, value INTEGER)")
        # Create a table for content storage
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS content (log_id INTEGER PRIMARY KEY, name TEXT, value BLOB, time INTEGER)"
        )

    # override is enforced
    def create_new_entry(self, entry_name, entry_url, entry_email, enforce=True):
        if not os.path.isfile(self.db_loc):
            self.initialize_default_db()
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM auth WHERE name=?", [entry_name])
        if cursor.fetchone() is not None and not enforce:
            return False

        cursor.execute("INSERT INTO auth VALUES(?, ?, ?)", [entry_name, entry_url, entry_email])
        cursor.execute("INSERT INTO counter VALUES(?, ?)", [entry_name, 0])
        db.commit()
        return True

    def remove_entry(self, entry_name):
        if not os.path.isfile(self.db_loc):
            self.initialize_default_db()
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM auth WHERE name=?", [entry_name])
        cursor.execute("DELETE FROM counter WHERE name=?", [entry_name])
        cursor.execute("DELETE FROM content WHERE name=?", [entry_name])
        db.commit()
        return True

    def add_new_log(self, entry_name, content):
        if not os.path.isfile(self.db_loc):
            self.initialize_default_db()
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM auth WHERE name=?", [entry_name])
        data = cursor.fetchone()
        if data is None:
            return False
        # Increment Counter
        cursor.execute("UPDATE counter SET value = value + 1 WHERE name=?", [entry_name])
        # Log query content
        t = int(time.time())
        cursor.execute("INSERT INTO content(name, value, time) VALUES(?, ?, ?)", [entry_name, content, t])
        db.commit()
        return True

    def get_all_entries(self):
        if not os.path.isfile(self.db_loc):
            self.initialize_default_db()
        db = self.get_db()
        cursor = db.cursor()
        ret = []
        cursor.execute("SELECT * FROM auth")
        data = cursor.fetchall()
        for entry in data:
            cur_entry = {}
            cur_entry['name'] = entry[0]
            cur_entry['url'] = entry[1]
            cur_entry['email'] = entry[2]
            ret.append(cur_entry)
        return ret

    # TODO: test
    def get_entry_count(self, entry_name):
        if not os.path.isfile(self.db_loc):
            self.initialize_default_db()
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute("SELECT value FROM counter WHERE name=?", [entry_name])
        data = cursor.fetchone()
        if data is None or len(data) < 1:
            return 0
        return int(data[0])

    # TODO: get log contents, enforce correct key
    def get_entry_logs(self, entry_name, entry_key):
        pass
