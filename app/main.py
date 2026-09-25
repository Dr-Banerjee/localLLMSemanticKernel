from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers.conversations_controller import ConversationsController
from controllers.sessions_controller import SessionsController
from auth.anonymous_session_service import AnonymousSessionService
from auth.current_user_dependency import CurrentUserDependency
from auth.current_user_service import CurrentUserService
from auth.session_token_service import SessionTokenService
from command_handlers.chat_command_handler import ChatCommandHandler
from config.settings import Settings
from db.database import Database
from db.unit_of_work_factory import UnitOfWorkFactory
from kernel.semantic_kernel_chat_completion import SemanticKernelChatCompletion
from query_handlers.conversation_messages_query_handler import ConversationMessagesQueryHandler
from query_handlers.conversation_summaries_query_handler import ConversationSummariesQueryHandler
from utils.mediator import Mediator

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

conversationsController = ConversationsController(
    mediator,
    currentUserDependency,
)
sessionsController = SessionsController(
    anonymousSessionService,
    currentUserDependency,
    settings,
)

app.include_router(conversationsController.router)
app.include_router(sessionsController.router)
