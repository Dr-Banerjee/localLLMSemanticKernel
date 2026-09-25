from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Session(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: UUID
