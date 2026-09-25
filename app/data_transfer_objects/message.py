from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Message(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    role: str
    content: str
    created_at: datetime
