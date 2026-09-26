from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChallengeProgress(BaseModel):

    user_id: UUID
    created_at: datetime
    updated_at: datetime
    challenge_step: int
