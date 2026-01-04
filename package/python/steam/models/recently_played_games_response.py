from pydantic import BaseModel, Field, ConfigDict


class RecentlyPlayedGamesResponse(BaseModel):
    model_config = ConfigDict(validate_by_name=True)

    app_id: int = Field(0, alias='appid')
    name: str
    playtime_2weeks: int
    playtime_forever: int
