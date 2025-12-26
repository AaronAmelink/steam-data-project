import os
from typing import Optional, Sequence

from dotenv import load_dotenv
import pyodbc
import polars as pl


class AzureSQLClient:
    def __init__(self, conn_string=None):
        load_dotenv()
        self.conn_string = (
            conn_string if conn_string else os.getenv("AZURE_SQL_CONN_STRING")
        )
        if not self.conn_string:
            raise ValueError(
                "Connection string not provided and AZURE_SQL_CONN_STRING not found in env."
            )
        self.conn = None
        self.cursor = None
        self.autocommit = True

    def connect(self):
        """Establish the database connection if not already connected."""
        if not self.conn:
            self.conn = pyodbc.connect(self.conn_string, autocommit=self.autocommit)
            self.cursor = self.conn.cursor()

    def set_autocommit(self, autocommit: bool):
        """Enable or disable autocommit."""
        self.autocommit = autocommit
        if self.conn:
            self.conn.autocommit = autocommit

    def query(self, query: str, params: Optional[Sequence] = None) -> pl.DataFrame:
        """
        Execute a SELECT query and return results as a Polars DataFrame.
        """
        self.connect()
        params = params or []

        self.cursor.execute(query, params if params else ())
        columns = [col[0] for col in self.cursor.description]
        rows = self.cursor.fetchall()

        if not rows:
            return pl.DataFrame(schema=columns)

        data = [dict(zip(columns, row)) for row in rows]
        return pl.DataFrame(data)

    def nonquery(self, query: str, params: Optional[Sequence] = None) -> int:
        """
        Execute an INSERT, UPDATE, DELETE, or DDL command.
        Returns the number of affected rows.
        """
        self.connect()
        params = params or []

        # Use executemany only if we have multiple rows of parameters
        if params and isinstance(params, list) and isinstance(params[0], (list, tuple)):
            self.cursor.executemany(query, params)
        else:
            self.cursor.execute(query, params if params else ())

        self.conn.commit()
        return self.cursor.rowcount

    def close(self):
        """Close the cursor and connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
