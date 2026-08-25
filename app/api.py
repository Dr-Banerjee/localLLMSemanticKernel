from fastapi import FastAPI
from models.request import UserRequest
import services.answer_service as answerService

app = FastAPI()

@app.post("/answer")
def get_answer(request: UserRequest):
    response = answerService.process(request)
    return response