from constants.exceptions import UserNotFoundError
from models.user import User
from steam.steam_client import SteamClient
from azure.azure_sql_client import AzureSQLClient


class UserHandler:
    def __init__(self):
        self.sql = AzureSQLClient()
        self.steam = SteamClient()

    async def __aenter__(self):
        pass

    async def __aexit__(self):
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
            raise UserNotFoundError("User not found")
        else:
            user = User(**(user))
        return user

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
            raise UserNotFoundError("User not found")
        else:
            user = User(**(user))
        return user
