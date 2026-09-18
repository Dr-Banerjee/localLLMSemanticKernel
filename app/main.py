from fastapi import FastAPI,Response, Depends, Query
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
from auth.anonymous_session_service import AnonymousSessionService
from db.models.user import User
from services.conversation_summaries_query_service import ConversationSummariesQueryService

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
    conversationSummariesQueryService = ConversationSummariesQueryService(unitOfWorkFactory)
    
    sessionTokenService = SessionTokenService()
    anonymousSessionService = AnonymousSessionService(
    unitOfWorkFactory,
    sessionTokenService,
    settings,
    )
    currentUserService = CurrentUserService(
        unitOfWorkFactory
    )
    currentUserDependency = CurrentUserDependency(
        currentUserService,
        sessionTokenService
    )

    #post endpoint to receive user input and return the response from the LLM for a single query
    @app.post("/answer")
    async def getAnswer(request: UserRequest):
        response = await answerService.processSingleRequest(request)    
        return response

    #post endpoint to carryout conversations with the LLM
    @app.post("/conversations/{conversationId}/messages")
    async def sendMessage(
        conversationId: int,
        request: UserRequest,
        currentUser: User = Depends(
                    currentUserDependency.resolveCurrentUser
                ),
    ):

        answer = await answerService.chatProcess(
            conversationId,
            request,
            currentUser.id
        )

        return answer
    @app.post("/session") #Need to move it to a new controller
    async def createSession(response: Response):
        sessionToken = await anonymousSessionService.createSession()
        response.set_cookie(
            key="session", #Make it configurable for prod it should be host session.
            value=sessionToken,
            httponly=True,
            secure=False, #Make it configurable for prod it should be True.
            samesite="lax",
            path="/",
            max_age=settings.anonymousSessionLifetimeDays*24*60*60            
        )
        return {"message": "Session created"}
    
    @app.get("/me") # Need to move it to a new Controller
    async def getCurrentUser(
        currentUser: User = Depends(
            currentUserDependency.resolveCurrentUser
        ),
    ):
        return {
            "id": str(currentUser.id),
        }
    @app.get("/conversations/summaries")
    async def getConversationSummaries(
        currentUser: User = Depends(
            currentUserDependency.resolveCurrentUser
        ),
        page : int = Query(default = 1, ge=1),
        pageSize: int = Query(default=20, ge=1, le=100),        
    ):
        return await conversationSummariesQueryService.getConversationSummaries( userId=currentUser.id,
                                                                                page=page,
                                                                                pageSize=pageSize
                                                                                )
    return app    