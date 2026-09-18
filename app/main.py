from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_transfer_objects.request import UserRequest
from data_transfer_objects.response import ResponseToUserRequest
from services.answer_service import AnswerService
import logging 
import sys
from db.database import Database
from config.settings import Settings
import os
from services.chat_service import ChatService
from db.repositories.conversation_repository import ConversationRepository
from services.single_chat_service import SingleChatService
from db.unit_of_work_factory import UnitOfWorkFactory
from auth.session_token_service import SessionTokenService
from auth.current_user_service import CurrentUserService
from auth.current_user_dependency import CurrentUserDependency

def createApp()-> FastAPI:

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
    settings = Settings()
    database = Database(
        settings.databaseUrl
    )
    unitOfWorkFactory = UnitOfWorkFactory(database)
    chatService = ChatService(unitOfWorkFactory)
    singleChatService = SingleChatService()
    answerService = AnswerService(chatService, singleChatService)
    sessionTokenService = SessionTokenService()
    currentUserService = CurrentUserService(
        unitOfWorkFactory
    )
    currentUserDependency = CurrentUserDependency(
        currentUserService,
        sessionTokenService
    )

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
    return app


