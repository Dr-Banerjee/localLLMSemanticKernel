from fastapi import FastAPI
from models.request import UserRequest
from models.response import ResponseToUserRequest
from services.answer_service import AnswerService
import logging 
import sys

# Configure application logging 
logging.basicConfig( level=logging.INFO, stream=sys.stdout, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", ) 
logger = logging.getLogger(__name__)

app = FastAPI()
answerService = AnswerService()

@app.get("/") 
async def root(): 
    logger.info("Root endpoint called") 
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
