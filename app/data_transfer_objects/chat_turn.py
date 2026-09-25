from pydantic import BaseModel, ConfigDict


class ChatTurn(BaseModel):
    model_config = ConfigDict(frozen=True)

    role: str
    content: str
