from fastapi import FastAPI
from models.request import UserRequest
from models.response import ResponseToUserRequest
import services.answer_service as answerService

app = FastAPI()

@app.post("/answer")
#post endpoint to receive user input and return the response from the LLM
async def get_answer(request: UserRequest):
    response = await answerService.process(request)    
    return response