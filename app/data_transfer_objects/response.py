from pydantic import BaseModel, ConfigDict

class ResponseToUserRequest(BaseModel):
    # makes it immutable and is almost like a record in C#
    model_config = ConfigDict(frozen=True)
    #The LLM's response.
    response: str