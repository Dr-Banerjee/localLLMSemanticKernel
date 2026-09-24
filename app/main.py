from fastapi import FastAPI, Response, Depends, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from services.conversation_messages_query_service import ConversationMessagesQueryService
from data_transfer_objects.request import UserRequest
from data_transfer_objects.response import ResponseToUserRequest
from services.answer_service import AnswerService
import logging 
import sys
from db.database import Database
from config.settings import Settings
import os
from services.chat_service import ChatService
from services.single_chat_service import SingleChatService
from db.unit_of_work_factory import UnitOfWorkFactory
from kernel.semantic_kernel_chat_completion import SemanticKernelChatCompletion
from auth.session_token_service import SessionTokenService
from auth.current_user_service import CurrentUserService
from auth.current_user_dependency import CurrentUserDependency
from auth.anonymous_session_service import AnonymousSessionService
from exceptions.exceptions import ConversationForbidden, ConversationNotFound
from models.user import User
from services.conversation_summaries_query_service import ConversationSummariesQueryService

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
chatCompletion = SemanticKernelChatCompletion()
chatService = ChatService(unitOfWorkFactory, chatCompletion)
singleChatService = SingleChatService(chatCompletion)
answerService = AnswerService(chatService, singleChatService)
conversationSummariesQueryService = ConversationSummariesQueryService(unitOfWorkFactory)
conversationMessagesQueryService = ConversationMessagesQueryService(unitOfWorkFactory)
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
@app.post("/api/conversations/answer")
async def getAnswer(request: UserRequest):
    response = await answerService.processSingleRequest(request)    
    return response

#post endpoint to carryout conversations with the LLM
@app.post("/api/conversations/{conversationId}/messages")
async def sendMessage(
    conversationId: int,
    request: UserRequest,
    currentUser: User = Depends(
                currentUserDependency.resolveCurrentUser
            ),
):

    try:
        answer = await answerService.chatProcess(
            conversationId,
            request,
            currentUser.id
        )
    except ConversationForbidden:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conversation does not belong to the current user",
        )

    return answer
@app.post("/api/sessions/session") #Need to move it to a new controller
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

@app.get("/api/sessions/me") # Need to move it to a new Controller
async def getCurrentUser(
    currentUser: User = Depends(
        currentUserDependency.resolveCurrentUser
    ),
):
    return {
        "id": str(currentUser.id),
    }
@app.get("/api/conversations/summaries")
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

@app.get("/api/conversations/{conversationId}/messages")
async def getConversationMessages(
    conversationId: int,
    currentUser: User = Depends(
        currentUserDependency.resolveCurrentUser
    ),
):
    try:
        return await conversationMessagesQueryService.getConversationMessages(
            conversationId=conversationId,
            userId=currentUser.id,
        )
    except ConversationNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )