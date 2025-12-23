import logging
from datetime import datetime
import pytz
import polars

from clients.azure.AzureSQLClient import AzureSQLClient
from clients.steam.SteamClient import SteamClient
from pipelines.classes.abstract_task import AbstractTask
from pipelines.utils.log_helper import configure_logger
from pipelines.utils.status_codes import StatusCode


class ImportUserData(AbstractTask):
    def __init__(self):
        self.sql = AzureSQLClient()
        self.steamClient = SteamClient()

    def get_users(self):
        """Fetch active users for the specified timezone."""
        users = self.sql.query("""
            SELECT 
                id,
                steam_id,
                timezone
            FROM dbo.user_accounts
            WHERE is_active = 1
        """)
        return users

    def insert_rows(self, rows):
        """Upsert rows into playtime_forever_historic."""
        time = datetime.now()

        query = """
            MERGE dbo.playtime_forever_historic AS target
            USING (VALUES (?, ?, ?, ?)) AS source (app_id, user_id, playtime_forever, recorded_at)
                ON target.app_id = source.app_id
                   AND target.user_id = source.user_id
                   AND target.playtime_forever = source.playtime_forever
            WHEN MATCHED THEN
                UPDATE SET recorded_at = source.recorded_at
            WHEN NOT MATCHED THEN
                INSERT (app_id, user_id, playtime_forever, recorded_at)
                VALUES (source.app_id, source.user_id, source.playtime_forever, source.recorded_at);
        """

        values = [
            (
                int(row['app_id']),
                int(row['user_id']),
                int(row['playtime_forever']),
                time
            )
            for row in rows.iter_rows(named=True)
        ]
        logging.info(f"Inserting {len(values)} rows into playtime_historic")
        self.sql.nonquery(query, values)

    def execute(self):
        users = self.get_users()

        if users.height == 0:
            logging.info(f"No users found")
            return StatusCode.NO_DATA

        for row in users.to_dicts():
            steam_id = row['steam_id']
            user_games = self.steamClient.get_recently_played_games(steam_id)
            if user_games.height == 0:
                logging.info(f"No recently played games found for user {steam_id}")
                continue
            user_games = user_games.with_columns(
                polars.lit(row['id']).alias('user_id')
            ).drop('playtime_2weeks')
            self.insert_rows(user_games)

        return StatusCode.SUCCESS


if __name__ == "__main__":
    configure_logger()
    pipeline = ImportUserData()
    pipeline.execute()
