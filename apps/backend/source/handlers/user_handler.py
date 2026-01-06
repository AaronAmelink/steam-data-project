from constants.exceptions import UserNotFoundError
from steam.models.steam_user import SteamUser
import logging
from models.user import User
from steam.steam_client import SteamClient
from azure.azure_sql_client import AzureSQLClient


class UserHandler:
    def __init__(self):
        self.sql = AzureSQLClient()
        self.steam = SteamClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.sql.conn:
            await self.sql.close()

    async def get_user(self, id: int) -> User:
        user = await self.sql.query_one(
            f"""
            SELECT
                is_active,
                steam_id,
                name,
                id,
                created_at,
                paused_at
            FROM user_accounts
            WHERE
                id = {id}
            """
        )

        if user is None:
            return None
        else:
            return User(**(user))

    async def create_user_from_steam(self, user: SteamUser) -> int:
        insert = f"""
        INSERT INTO user_accounts
            (
                steam_id,
                name
            )
        OUTPUT INSERTED.id
        VALUES
            (
                {user.steam_id},
                '{user.name}'
            )
        """
        res = await self.sql.query_one(insert)
        logging.info(f"Inserted user: {res}")
        if not res['id']:
            raise Exception("Could not insert new user")

        return res['id']

    async def get_user_by_steam_id(self, steam_id: int) -> User:
        user = await self.sql.query_one(
            f"""
            SELECT
                is_active,
                steam_id,
                name,
                id,
                created_at,
                paused_at
            FROM user_accounts
            WHERE
                steam_id = {steam_id}
            """
        )

        if user is None:
            return None
        else:
            return User(**(user))
