from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ConversationMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    role: str
    content: str
    createdAt: datetime
