import sqlite3


class DB(object):

    def __init__(self, name, table_schema):
        self._name = name
        self._table_schema = table_schema

    def _open_connection(self):
        self._connection = sqlite3.connect(self._name)

    def _close_connection(self):
        self._connection.close()

    def _commit_changes(self):
        self._connection.commit()

    def _init_table(self):
        self._connection.execute(self._table_schema)

    def execute(self, operation, entities):
        try:
            self._open_connection()
            self._init_table()

            for entity in entities:
                self._connection.execute(operation, entity)

            self._commit_changes()
        except Exception as e:
            print(e)
        finally:
            self._close_connection()



