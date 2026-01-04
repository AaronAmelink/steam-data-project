from pydantic import BaseModel, ConfigDict, Field


class AuthedJWT(BaseModel):
    model_config = ConfigDict(validate_by_name=True)

    id: str = Field(alias='sub')
    steam_id: str
