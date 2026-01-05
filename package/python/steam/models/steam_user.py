from pydantic import BaseModel, Field, ConfigDict, field_serializer, field_validator
from enum import IntEnum
from datetime import datetime


class CommunityVisibilityState(IntEnum):
    PRIVATE = 1
    PUBLIC = 3


class SteamUser(BaseModel):
    model_config = ConfigDict(validate_by_name=True)

    steam_id: str = Field(alias='steamid')
    community_visibility_state: CommunityVisibilityState = Field(alias='communityvisibilitystate')
    avatar_url: str = Field(alias='avatar')
    name: str = Field(alias='personaname')
    last_log_off: datetime = Field(alias='lastlogoff')

    @field_serializer("community_visibility_state")
    def convert_to_text(self, value: CommunityVisibilityState):
        return value.name.lower()
