from pydantic import BaseModel

class ResponseToUserRequest(BaseModel):
    #The meaning of the idiom
    meaning: str
    #The reason why the idiom means so
    reason: str
    #an example of the idiom being used
    example: str
    #small sentence that will help the kid remember the idiom
    #and it's meaning
    remember: str