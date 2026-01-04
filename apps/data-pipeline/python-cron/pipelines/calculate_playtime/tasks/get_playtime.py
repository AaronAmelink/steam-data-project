import logging
import asyncio
from azure.azure_sql_client import AzureSQLClient
from steam.steam_client import SteamClient
from pipelines.utils.log_helper import configure_logger
from pipelines.utils.status_codes import StatusCode
from pipelines.classes.abstract_task import AbstractTask


class GetPlaytime(AbstractTask):
    def __init__(self, sql: AzureSQLClient):
        self.sql = sql
        self.steamClient = SteamClient()

    async def get_insert_playtime_data(self) -> int:
        # Use CAST(recorded_at AS DATE) to only consider the local day
        query = """
        WITH RankedPlaytime AS (
            SELECT
                app_id,
                playtime_forever,
                recorded_at,
                user_id,
                ROW_NUMBER() OVER (PARTITION BY user_id, app_id ORDER BY recorded_at DESC) AS rn
            FROM playtime_forever_historic
                     LEFT JOIN dbo.user_accounts ua ON ua.id = playtime_forever_historic.user_id
            WHERE ua.is_active = 1
        ),
        Today AS (
            SELECT *
            FROM RankedPlaytime
            WHERE rn = 1
        ),
        Last AS (
            SELECT *
            FROM RankedPlaytime
            WHERE rn = 2
        ),
        PlaytimeDelta AS (
            SELECT
                t.app_id,
                t.user_id,
                t.playtime_forever - l.playtime_forever AS playtime_delta,
                GETDATE() AS recorded_at
            FROM Today t
            INNER JOIN Last l
                ON t.app_id = l.app_id
                AND t.user_id = l.user_id
            WHERE t.playtime_forever - l.playtime_forever <> 0
        )
        INSERT INTO playtime_calculated (
            app_id,
            user_id,
            playtime_delta,
            recorded_at
        )
        SELECT
            app_id,
            user_id,
            playtime_delta,
            recorded_at
        FROM PlaytimeDelta;
        """
        return await self.sql.nonquery(query)

    async def execute(self):
        inserts = await self.get_insert_playtime_data()
        await self.sql.close()
        logging.info(f"Inserted {inserts} daily playtime records successfully.")

        return StatusCode.SUCCESS


if __name__ == "__main__":
    configure_logger()
    with AzureSQLClient() as sql:
        pipeline = GetPlaytime(sql)
        asyncio.run(pipeline.execute())
