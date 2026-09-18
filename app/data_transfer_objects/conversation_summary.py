from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ConversationSummary(BaseModel):
        model_config = ConfigDict(frozen=True)
        
        id: int
        createdAt: datetime
        updatedAt: datetime
        initialMessage: str