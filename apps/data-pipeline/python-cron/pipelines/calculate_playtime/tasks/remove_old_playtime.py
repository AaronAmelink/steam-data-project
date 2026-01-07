import logging
import asyncio
from azure.azure_sql_client import AzureSQLClient
from pipelines.classes.abstract_task import AbstractTask
from pipelines.utils.log_helper import configure_logger
from pipelines.utils.status_codes import StatusCode


class RemoveOldPlaytime(AbstractTask):
    def __init__(self, sql: AzureSQLClient):
        self.sql = sql

    async def remove_old_records(self):
        """
        Removes all but the most recent historic entry per user/app_id combination.
        """
        # SQL deletes everything except the latest record per user_id/app_id
        query = """
        WITH RankedHistoric AS (
            SELECT
                id,
                user_id,
                app_id,
                recorded_at,
                ROW_NUMBER() OVER (PARTITION BY user_id, app_id ORDER BY recorded_at DESC) AS rn
            FROM playtime_forever_historic
        )
        DELETE FROM playtime_forever_historic
        WHERE id IN (
            SELECT id
            FROM RankedHistoric
            WHERE rn > 1
        );
        """
        deleted_rows = await self.sql.nonquery(query)
        logging.info(f"Removed all but the latest historic record per user/app_id: {deleted_rows}")

    async def execute(self):
        logging.info("Starting cleanup of historic playtime data...")
        await self.remove_old_records()
        logging.info("Historic data cleanup complete.")

        return StatusCode.SUCCESS


if __name__ == "__main__":
    configure_logger()
    with AzureSQLClient() as sql:
        pipeline = RemoveOldPlaytime(sql)
        asyncio.run(pipeline.execute())
