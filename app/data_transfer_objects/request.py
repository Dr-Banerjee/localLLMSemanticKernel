from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    userInput: str = Field(min_length=1, max_length=500)
    language: Literal["en", "de"] = "en"
