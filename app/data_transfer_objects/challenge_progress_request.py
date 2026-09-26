from pydantic import BaseModel, ConfigDict


class ChallengeProgressRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    challenge_step: int
