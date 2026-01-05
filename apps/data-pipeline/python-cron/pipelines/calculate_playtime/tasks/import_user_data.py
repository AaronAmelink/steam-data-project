import logging
from datetime import datetime
from azure.azure_sql_client import AzureSQLClient
import polars as pl
from steam.steam_client import SteamClient
from pipelines.classes.abstract_task import AbstractTask
from pipelines.utils.log_helper import configure_logger
from pipelines.utils.status_codes import StatusCode
import asyncio


class ImportUserData(AbstractTask):
    def __init__(self, sql: AzureSQLClient):
        self.sql = sql
        self.steamClient = SteamClient()

    async def get_users(self):
        """Fetch active users for the specified timezone."""
        users = await self.sql.query("""
            SELECT 
                id,
                steam_id,
                last_log_off
            FROM user_accounts
            WHERE is_active = 1
        """)
        return users

    async def check_user_activity(self, users: list[dict]):
        """
        Check that users have playtime since last logged
        do this because we can batch this by up to 100 people,
        saving up to 99 calls sometimes
        """
        # last log off is a misleading name
        # per steam docs:
        # The last time the user was online, in unix time.

        calls = []
        for i in range(0, len(users), 100):
            batch = users[i:i+100]
            calls.append(self.steamClient.get_steam_users_raw([user['steam_id'] for user in batch]))

        results = await asyncio.gather(*calls)
        flattended = []
        for batch in results:
            flattended.extend(batch)
        df = pl.DataFrame(flattended)

        steam_to_user = {user['steam_id']: user['id'] for user in users}

        df = df.with_columns([
            pl.Series('id', [steam_to_user.get(str(sid)) for sid in df['steamid']]),
            (pl.col('profilestate') == 1).cast(pl.Int8).alias('is_active'),
            pl.from_epoch("lastlogoff", time_unit="s").alias("last_log_off")
        ])

        df = df.with_columns([
            pl.col('steamid').alias('steam_id')
        ])

        disable_accounts = [str(account['id']) for account in df.to_dicts() if not account['is_active']]
        if len(disable_accounts) != 0:
            query = f"""
            UPDATE user_accounts
            SET is_active = 0
            WHERE
                id IN ({','.join(disable_accounts)})
            """

            await self.sql.nonquery(query)

        logging.info(users)

        db_last_log_off = {user['id']: user['last_log_off'] for user in users}

        df = df.with_columns(
            pl.col("id")
            .map_elements(lambda x: db_last_log_off.get(x))
            .alias("db_last_log_off")
        )

        df = df.with_columns(
            (pl.col("last_log_off") != pl.col("db_last_log_off"))
            .fill_null(False)
            .alias("last_log_off_changed")
        )

        changed_users = df.filter(pl.col('last_log_off_changed')).to_dicts()

        # Update DB: last_log_off and is_active
        for user in changed_users:
            await self.sql.nonquery("""
                UPDATE user_accounts
                SET last_log_off = ?
                WHERE id = ?
            """, (user['last_log_off'], user['id']))

        return changed_users

    async def insert_rows(self, all_games):
        """Insert all game rows into SQL in a single batch."""
        combined_games = pl.concat(all_games)
        time = datetime.now()
        values = [
            (
                int(row['app_id']),
                int(row['user_id']),
                int(row['playtime_forever']),
                time
            )
            for row in combined_games.iter_rows(named=True)
        ]

        logging.info(f"Inserting {len(values)} rows into playtime_historic in a single batch")
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
        await self.sql.nonquery(query, values)

    async def fetch_all_users_games(self, users):
        """Fetch recently played games for all users in parallel."""
        async def fetch_user_games(row):
            steam_id = row['steam_id']
            user_games = await self.steamClient.get_recently_played_games(steam_id)
            if user_games.height == 0:
                logging.info(f"No recently played games found for user {steam_id}")
                return None
            return user_games.with_columns(
                pl.lit(row['id']).alias('user_id')
            ).drop('playtime_2weeks')

        user_games_list = await asyncio.gather(*(fetch_user_games(u) for u in users))
        return [g for g in user_games_list if g is not None]

    async def execute(self):
        users = await self.get_users()

        if len(users) == 0:
            logging.info("No users found")
            return StatusCode.NO_DATA

        changed_users = await self.check_user_activity(users)

        if len(changed_users) == 0:
            logging.info("No user activity")
            return StatusCode.NO_DATA

        games = await self.fetch_all_users_games(self, changed_users)
        if not games:
            logging.info("No games to insert")
            return StatusCode.NO_DATA

        await self.insert_rows(games)
        return StatusCode.SUCCESS



if __name__ == "__main__":
    configure_logger()
    with AzureSQLClient() as sql:
        pipeline = ImportUserData(sql)
        asyncio.run(pipeline.execute())
