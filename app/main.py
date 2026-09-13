from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_transfer_objects.request import UserRequest
from data_transfer_objects.response import ResponseToUserRequest
from services.answer_service import AnswerService
import logging 
import sys

# Configure application logging 
logging.basicConfig( level=logging.INFO, stream=sys.stdout, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", ) 
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
    conversationId: int,
    request: UserRequest,
):

    answer = await answerService.chatProcess(
        conversationId,
        request,
    )

    return answer
