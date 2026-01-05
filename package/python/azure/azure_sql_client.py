import os
from typing import Optional, Sequence
from dotenv import load_dotenv
import aioodbc


class AzureSQLClient:
    def __init__(self, conn_string: Optional[str] = None):
        load_dotenv()
        self.conn_string = conn_string or os.getenv("AZURE_SQL_CONN_STRING")
        if not self.conn_string:
            raise ValueError(
                "Connection string not provided and AZURE_SQL_CONN_STRING not found in env."
            )
        self.conn = None
        self.cursor = None
        self.autocommit = True

    async def __aexit(self):
        if self.conn:
            await self.close()

    async def connect(self):
        """Establish the database connection if not already connected."""
        if not self.conn:
            self.conn = await aioodbc.connect(
                dsn=self.conn_string, autocommit=self.autocommit
            )
            self.cursor = await self.conn.cursor()

    async def set_autocommit(self, autocommit: bool):
        """Enable or disable autocommit."""
        self.autocommit = autocommit
        if self.conn:
            self.conn.autocommit = autocommit

    async def query(self, query: str, params: Optional[Sequence] = None) -> list:
        """
        Execute a SELECT query and return results as a Polars DataFrame.
        """
        await self.connect()
        params = params or []

        await self.cursor.execute(query, params if params else ())
        columns = [desc[0] for desc in self.cursor.description]
        rows = await self.cursor.fetchall()

        if not rows:
            return []

        data = [dict(zip(columns, row)) for row in rows]
        return data

    async def query_one(self, query: str, params: Optional[Sequence] = None) -> dict | None:
        res = await self.query(query, params)
        return res[0] if len(res) > 0 else None

    async def nonquery(self, query: str, params: Optional[Sequence] = None) -> int:
        """
        Execute an INSERT, UPDATE, DELETE, or DDL command.
        Returns the number of affected rows.
        """
        await self.connect()
        params = params or []

        if params and isinstance(params, list) and isinstance(params[0], (list, tuple)):
            await self.cursor.executemany(query, params)
        else:
            await self.cursor.execute(query, params if params else ())

        await self.conn.commit()
        return self.cursor.rowcount

    async def close(self):
        """Close the cursor and connection."""
        if self.cursor:
            await self.cursor.close()
        if self.conn:
            await self.conn.close()
        self.conn = None
        self.cursor = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
        return
