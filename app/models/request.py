from pydantic import BaseModel

class UserRequest(BaseModel):
    userInput: str