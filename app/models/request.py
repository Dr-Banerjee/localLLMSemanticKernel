from pydantic import BaseModel

class UserRequest(BaseModel):
    #The string supplied by the user as input.
    userInput: str