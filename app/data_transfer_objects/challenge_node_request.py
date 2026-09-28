from typing import Literal

from pydantic import BaseModel, ConfigDict


class ChallengeNodeRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_id: int
    conversation_id: int
    language: Literal["en", "de"] = "en"
