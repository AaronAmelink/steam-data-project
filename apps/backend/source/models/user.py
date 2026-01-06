from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class User(BaseModel):
    model_config = ConfigDict(validate_by_name=True)

    id: int
    steam_id: int
    name: str
    created_at: datetime
    paused_at: Optional[datetime]
    is_active: bool
