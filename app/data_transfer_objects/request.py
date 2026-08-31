from pydantic import BaseModel, ConfigDict

class UserRequest(BaseModel):
    # makes it immutable and is almost like a record in C#
    model_config = ConfigDict(frozen=True)
    
    #The string supplied by the user as input.
    userInput: str