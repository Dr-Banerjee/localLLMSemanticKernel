from pydantic import BaseModel, ConfigDict


class ChallengeNodeConversation(BaseModel):
    model_config = ConfigDict(frozen=True)

    conversation_id: int
