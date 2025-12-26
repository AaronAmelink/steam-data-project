import os
from dotenv import load_dotenv
from clients.steam.models.RecentlyPlayedGamesResponse import RecentlyPlayedGamesResponse
import requests
import polars as pl
from urllib.parse import urlencode


class SteamClient:
    BASE_URL = 'http://api.steampowered.com'
    STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"

    def __init__(self, api_key=None):
        load_dotenv()
        self.api_key = api_key if api_key else os.getenv("STEAM_API_KEY")
        if not self.api_key:
            raise ValueError("No Steam API Key provided.")

    def get_recently_played_games(self, id64) -> pl.DataFrame:
        url = f"{self.BASE_URL}/IPlayerService/GetRecentlyPlayedGames/v1/"
        params = {
            'key': self.api_key,
            'steamid': id64,
            'format': 'json'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return pl.DataFrame([RecentlyPlayedGamesResponse.from_dict(game) for game in response.json().get('response', {}).get('games', [])])
        else:
            response.raise_for_status()
            return pl.DataFrame([])

    @classmethod
    def get_steam_login_url(cls, return_to: str, realm: str) -> str:
        """
        Generates Steam OpenID login URL
        """
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
    def verify_steam_openid(cls, params: dict) -> str | None:
        """
        Verifies the OpenID response and extracts SteamID
        """
        # Prepare verification request
        verification_params = dict(params)
        verification_params["openid.mode"] = "check_authentication"

        response = requests.post(cls.STEAM_OPENID_URL, data=verification_params)
        response_text = response.text

        if "is_valid:true" not in response_text:
            return None

        # Extract SteamID
        claimed_id = params.get("openid.claimed_id")
        if not claimed_id:
            return None

        # SteamID is the last part of the URL
        return claimed_id.split("/")[-1]
