import sqlite3


class SQLFork:
    def __init__(self, mode):
        self.connection = self.connect()
        self.cursor = self.connection.cursor()
        self.mode = mode

    @staticmethod
    def connect():
        with sqlite3.connect('onyx.db') as connection:
            return connection

    def execute_sql(self, query):
        match self.mode:
            case 'SELECT':
                self.cursor.execute(query)
                return self.cursor.fetchall()

            case 'INSERT' | 'UPDATE' | 'DELETE':
                self.cursor.execute(query)
                self.connection.commit()
