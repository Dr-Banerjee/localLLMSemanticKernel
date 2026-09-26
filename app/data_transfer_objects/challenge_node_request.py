from pydantic import BaseModel, ConfigDict


class ChallengeNodeRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_id: int
