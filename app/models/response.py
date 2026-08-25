from pydantic import BaseModel

class ResponseToUserRequest(BaseModel):
    #The string generated as response to the user input.
    responseToUserRequest: str