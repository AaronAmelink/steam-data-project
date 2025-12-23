from dataclasses import dataclass
from typing import override
from clients.Model import Model


@dataclass
class RecentlyPlayedGamesResponse(Model):
    app_id: int
    name: str
    playtime_2weeks: int
    playtime_forever: int

    @staticmethod
    @override
    def from_dict(data):
        return RecentlyPlayedGamesResponse(
            app_id=data.get("appid", 0),
            name=data.get("name", ""),
            playtime_2weeks=data.get("playtime_2weeks", 0),
            playtime_forever=data.get("playtime_forever", 0),
        )
