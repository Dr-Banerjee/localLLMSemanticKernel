from fastapi import FastAPI
from models.request import UserRequest
from models.response import ResponseToUserRequest
import services.answer_service as answerService
import logging 
import sys
# Configure application logging 
logging.basicConfig( level=logging.INFO, stream=sys.stdout, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", ) 
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/") 
async def root(): 
    logger.info("Root endpoint called") 
    return {"message": "Hello World"}

@app.post("/answer")
#post endpoint to receive user input and return the response from the LLM
async def get_answer(request: UserRequest):
    response = await answerService.process(request)    
    return response
@app.post("/conversations/{conversationId}/messages")
async def send_message(
    conversationId: str,
    request: UserRequest,
):

    answer = await answerService.chatProcess(
        conversationId,
        request,
    )

    return {
        "answer": answer
    }
