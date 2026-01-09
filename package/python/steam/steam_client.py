from steam.models.steam_user import SteamUser
import os
import asyncio
import httpx
import polars as pl
from dotenv import load_dotenv
from urllib.parse import urlencode
from steam.models.recently_played_games_response import RecentlyPlayedGamesResponse


class SteamClient:
    BASE_URL = "https://api.steampowered.com"
    STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"

    MAX_RETRIES = 5
    BASE_BACKOFF = 0.5  # seconds

    def __init__(self, api_key: str | None = None):
        load_dotenv()
        self.api_key = api_key or os.getenv("STEAM_API_KEY")
        if not self.api_key:
            raise ValueError("No Steam API Key provided.")

        self.client = httpx.AsyncClient(
            timeout=10,
            headers={"User-Agent": "FastAPI-SteamClient"}
        )

    async def close(self):
        await self.client.aclose()

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        data: dict | None = None,
    ) -> httpx.Response:

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = await self.client.request(
                    method,
                    url,
                    params=params,
                    data=data,
                )

                # Rate limited
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    wait_time = float(retry_after) if retry_after else self.BASE_BACKOFF * (2 ** (attempt - 1))
                    await asyncio.sleep(wait_time)
                    continue

                # Retry on transient server errors
                if response.status_code >= 500:
                    await asyncio.sleep(self.BASE_BACKOFF * (2 ** (attempt - 1)))
                    continue

                response.raise_for_status()
                return response

            except httpx.RequestError:
                # Network issue
                if attempt == self.MAX_RETRIES:
                    raise
                await asyncio.sleep(self.BASE_BACKOFF * (2 ** (attempt - 1)))

        raise RuntimeError("Max retries exceeded")

    # --------------------------------------------------
    # Steam Web API
    # --------------------------------------------------

    @classmethod
    def map_img_icon_hash_to_url(cls, app_id:str, hash:str) -> str:
        return f"http://media.steampowered.com/steamcommunity/public/images/apps/{app_id}/{hash}.jpg"

    async def get_recently_played_games(self, id64: str) -> pl.DataFrame:
        url = f"{self.BASE_URL}/IPlayerService/GetRecentlyPlayedGames/v1/"
        params = {
            "key": self.api_key,
            "steamid": id64,
            "format": "json",
        }

        response = await self._request("GET", url, params=params)
        games = response.json().get("response", {}).get("games", [])

        return pl.DataFrame(games).rename({'appid': 'app_id'})

    async def get_steam_users_raw(self, ids: list[str]) -> list[dict]:
        url = f"{self.BASE_URL}/ISteamUser/GetPlayerSummaries/v2/"
        params = {
            "key": self.api_key,
            "steamids": ",".join([str(id) for id in ids]),
        }

        response = await self._request("GET", url, params=params)
        players = response.json()["response"]["players"]
        return players

    async def get_steam_users(self, ids: list[str]) -> list[SteamUser]:
        players = await self.get_steam_users_raw(ids)
        return [SteamUser(**p) for p in players]

    async def get_steam_user(self, steam_id: str) -> SteamUser | None:
        users = await self.get_steam_users([steam_id])
        return users[0] if users else None

    # --------------------------------------------------
    # OpenID
    # --------------------------------------------------

    @classmethod
    def get_steam_login_url(cls, return_to: str, realm: str) -> str:
        params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": return_to,
            "openid.realm": realm,
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }
        return f"{cls.STEAM_OPENID_URL}?{urlencode(params)}"

    @classmethod
    async def verify_steam_openid(cls, params: dict) -> str | None:
        verification_params = dict(params)
        verification_params["openid.mode"] = "check_authentication"

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                cls.STEAM_OPENID_URL,
                data=verification_params,
            )

        if "is_valid:true" not in response.text:
            return None

        claimed_id = params.get("openid.claimed_id")
        return claimed_id.split("/")[-1] if claimed_id else None

