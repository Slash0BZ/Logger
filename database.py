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
        cursor.execute("CREATE TABLE IF NOT EXISTS auth (name TEXT PRIMARY KEY, value TEXT)")
        # Create a table for counter storage
        cursor.execute("CREATE TABLE IF NOT EXISTS counter (name TEXT PRIMARY KEY, value INTEGER)")

    def create_new_entry(self, entry_name, entry_key):
        if not os.path.isfile(self.db_loc):
            self.initialize_default_db()
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM auth WHERE name=?", [entry_name])
        if cursor.fetchone() is not None:
            return False

        cursor.execute("INSERT INTO auth VALUES(?, ?)", [entry_name, entry_key])
        cursor.execute("INSERT INTO counter VALUES(?, ?)", [entry_name, 0])
        cursor.execute("CREATE TABLE IF NOT EXISTS " + entry_name + " (content BLOB, time INTEGER)")
        db.commit()
        return True

    def add_new_log(self, entry_name, entry_key, content):
        if not os.path.isfile(self.db_loc):
            self.initialize_default_db()
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute("SELECT value FROM auth WHERE name=?", [entry_name])
        data = cursor.fetchone()
        if data is None:
            return False
        # Check if the API request is legal
        if entry_key != data[0]:
            return False
        # Increment Counter
        cursor.execute("UPDATE counter SET value = value + 1 WHERE name=?", [entry_name])
        # Log query content
        t = int(time.time())
        query = 'INSERT INTO {} VALUES ("{}", {})'.format(entry_name, content, t)
        cursor.execute(query)
        db.commit()
        return True

    # TODO: Finish counter, return a int
    def get_entry_count(self, entry_name):
        pass

    # TODO: get log contents, enforce correct key
    def get_entry_logs(self, entry_name, entry_key):
        pass
