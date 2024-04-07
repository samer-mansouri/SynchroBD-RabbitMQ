import mysql.connector

class DatabaseManager:
    def __init__(self, config):
        self.config = config

    def execute(self, query, params=None, commit=False, fetch=False):
        with mysql.connector.connect(**self.config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            if commit:
                conn.commit()
            if fetch:
                return cursor.fetchall()
            
    def insert(self, query, params):
        with mysql.connector.connect(**self.config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid