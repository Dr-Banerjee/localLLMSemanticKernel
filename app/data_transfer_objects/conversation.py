from pydantic import BaseModel, ConfigDict


class Conversation(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
