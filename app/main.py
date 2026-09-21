from fastapi import FastAPI, Response, Depends, Query, HTTPException, status
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
from data_transfer_objects.conversation_message import ConversationMessage



app = FastAPI()    
settings = Settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.corsAllowedOrigins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
    sessionTokenService,
    settings
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
        key=settings.sessionCookieName,
        value=sessionToken,
        httponly=True,
        secure=settings.sessionCookieSecure,
        samesite=settings.sessionCookieSameSite,
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

@app.get("/conversations/{conversationId}/messages")
async def getConversationMessages(
    conversationId: int,
    currentUser: User = Depends(
        currentUserDependency.resolveCurrentUser
    ),
):
    async with unitOfWorkFactory.create() as unitOfWork:
        conversation = await unitOfWork.conversationRepository.getConversation(
            conversationId,
            currentUser.id,
        )
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
        messages = await unitOfWork.conversationRepository.getMessages(
            conversationId,
            currentUser.id,
        )
        return [
            ConversationMessage(
                id=message.id,
                role=message.role,
                content=message.content,
                createdAt=message.created_at,
            )
            for message in messages
        ]

       