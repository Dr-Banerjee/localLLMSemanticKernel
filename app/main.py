from fastapi import FastAPI
from app.data_transfer_objects.request import UserRequest
from app.data_transfer_objects.response import ResponseToUserRequest
from app.services.answer_service import AnswerService
import logging 
import sys



app = FastAPI()
answerService = AnswerService()

@app.get("/") 
async def root(): 
    return {"message": "Hello World"}

#post endpoint to receive user input and return the response from the LLM for a single query
@app.post("/answer")
async def get_answer(request: UserRequest):
    response = await answerService.processSingleRequest(request)    
    return response

#post endpoint to carryout conversations with the LLM
@app.post("/conversations/{conversationId}/messages")
async def send_message(
    conversationId: str,
    request: UserRequest,
):

    answer = await answerService.chatProcess(
        conversationId,
        request,
    )

    return answer
