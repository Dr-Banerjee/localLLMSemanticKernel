from fastapi import FastAPI, Response, Depends, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from queries.conversationMessagesQuery import ConversationMessagesQuery
from commands.chat_command import ChatCommand
from queries.conversationSummariesQuery import ConversationSummariesQuery
from query_handlers.conversation_messages_query_handler import ConversationMessagesQueryHandler
from data_transfer_objects.request import UserRequest
from utils.mediator import Mediator
from db.database import Database
from config.settings import Settings
from command_handlers.chat_command_handler import ChatCommandHandler
from db.unit_of_work_factory import UnitOfWorkFactory
from kernel.semantic_kernel_chat_completion import SemanticKernelChatCompletion
from auth.session_token_service import SessionTokenService
from auth.current_user_service import CurrentUserService
from auth.current_user_dependency import CurrentUserDependency
from auth.anonymous_session_service import AnonymousSessionService
from exceptions.conversation_forbidden_exception import ConversationForbiddenException
from exceptions.conversation_not_found_exception import ConversationNotFoundException
from models.user import User
from query_handlers.conversation_summaries_query_handler import ConversationSummariesQueryHandler

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
chatCommandHandler = ChatCommandHandler(unitOfWorkFactory, chatCompletion)
conversationSummariesQueryHandler = ConversationSummariesQueryHandler(unitOfWorkFactory)
conversationMessagesQueryHandler = ConversationMessagesQueryHandler(unitOfWorkFactory)
mediator = Mediator(
    chatCommandHandler,
    conversationSummariesQueryHandler,
    conversationMessagesQueryHandler,
)
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

@app.post("/api/conversations/{conversationId}/messages")
async def sendMessage(
    conversationId: int,
    request: UserRequest,
    currentUser: User = Depends(
        currentUserDependency.resolveCurrentUser
    ),
):
    try:
        answer = await mediator.send(ChatCommand(conversationId,
                    request,
                    currentUser.id)            
        )
    except ConversationForbiddenException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conversation does not belong to the current user",
        )

    return answer

@app.post("/api/sessions/session")
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

@app.get("/api/sessions/me")
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
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    return await mediator.send(ConversationSummariesQuery(
        userId=currentUser.id,
                page=page,
                pageSize=pageSize,
    )        
    )

@app.get("/api/conversations/{conversationId}/messages")
async def getConversationMessages(
    conversationId: int,
    currentUser: User = Depends(
        currentUserDependency.resolveCurrentUser
    ),
):
    try:
        return await mediator.send(ConversationMessagesQuery(
            conversationId=conversationId,
            userId=currentUser.id,
        )            
        )
    except ConversationNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
