from abstractions.i_command import ICommand
from abstractions.i_query import IQuery
from commands.chat_command import ChatCommand
from commands.create_challenge_progress_command import CreateChallengeProgressCommand
from commands.delete_conversation_command import DeleteConversationCommand
from commands.start_challenge_node_command import StartChallengeNodeCommand
from commands.update_challenge_progress_command import UpdateChallengeProgressCommand
from queries.challenge_progress_query import ChallengeProgressQuery
from queries.open_visited_challenge_node_query import OpenVisitedChallengeNodeQuery
from queries.conversationMessagesQuery import ConversationMessagesQuery
from queries.conversationSummariesQuery import ConversationSummariesQuery
from command_handlers.chat_command_handler import ChatCommandHandler
from command_handlers.create_challenge_progress_command_handler import (
    CreateChallengeProgressCommandHandler,
)
from command_handlers.delete_conversation_command_handler import (
    DeleteConversationCommandHandler,
)
from command_handlers.start_challenge_node_command_handler import (
    StartChallengeNodeCommandHandler,
)
from command_handlers.update_challenge_progress_command_handler import (
    UpdateChallengeProgressCommandHandler,
)
from query_handlers.challenge_progress_query_handler import ChallengeProgressQueryHandler
from query_handlers.conversation_messages_query_handler import ConversationMessagesQueryHandler
from query_handlers.conversation_summaries_query_handler import ConversationSummariesQueryHandler
from query_handlers.open_visited_challenge_node_query_handler import (
    OpenVisitedChallengeNodeQueryHandler,
)


class Mediator:
    def __init__(
        self,
        chatCommandHandler: ChatCommandHandler,
        conversationSummariesQueryHandler: ConversationSummariesQueryHandler,
        conversationMessagesQueryHandler: ConversationMessagesQueryHandler,
        deleteConversationCommandHandler: DeleteConversationCommandHandler,
        createChallengeProgressCommandHandler: CreateChallengeProgressCommandHandler,
        updateChallengeProgressCommandHandler: UpdateChallengeProgressCommandHandler,
        challengeProgressQueryHandler: ChallengeProgressQueryHandler,
        startChallengeNodeCommandHandler: StartChallengeNodeCommandHandler,
        openVisitedChallengeNodeQueryHandler: OpenVisitedChallengeNodeQueryHandler,
    ) -> None:
        self.chatCommandHandler = chatCommandHandler
        self.conversationSummariesQueryHandler = conversationSummariesQueryHandler
        self.conversationMessagesQueryHandler = conversationMessagesQueryHandler
        self.deleteConversationCommandHandler = deleteConversationCommandHandler
        self.createChallengeProgressCommandHandler = createChallengeProgressCommandHandler
        self.updateChallengeProgressCommandHandler = updateChallengeProgressCommandHandler
        self.challengeProgressQueryHandler = challengeProgressQueryHandler
        self.startChallengeNodeCommandHandler = startChallengeNodeCommandHandler
        self.openVisitedChallengeNodeQueryHandler = openVisitedChallengeNodeQueryHandler

    async def send(self, commandOrQuery: ICommand | IQuery):
        match commandOrQuery:
            case ChatCommand():
                return await self.chatCommandHandler.handleChatCommand(
                    commandOrQuery.conversationId,
                    commandOrQuery.request,
                    commandOrQuery.userId,
                )
            case DeleteConversationCommand():
                return await self.deleteConversationCommandHandler.handleDeleteConversationCommand(
                    commandOrQuery.conversationId,
                    commandOrQuery.userId,
                )
            case ConversationMessagesQuery():
                return await self.conversationMessagesQueryHandler.handleConversationMessagesQuery(
                    commandOrQuery.conversationId,
                    commandOrQuery.userId,
                )
            case ConversationSummariesQuery():
                return await self.conversationSummariesQueryHandler.handleConversationSummariesQuery(
                    commandOrQuery.userId,
                    commandOrQuery.page,
                    commandOrQuery.pageSize,
                )
            case CreateChallengeProgressCommand():
                return await self.createChallengeProgressCommandHandler.handleCreateChallengeProgressCommand(
                    commandOrQuery.userId,
                    commandOrQuery.challengeStep,
                )
            case UpdateChallengeProgressCommand():
                return await self.updateChallengeProgressCommandHandler.handleUpdateChallengeProgressCommand(
                    commandOrQuery.userId,
                    commandOrQuery.challengeStep,
                )
            case ChallengeProgressQuery():
                return await self.challengeProgressQueryHandler.handleChallengeProgressQuery(
                    commandOrQuery.userId,
                )
            case StartChallengeNodeCommand():
                return await self.startChallengeNodeCommandHandler.handleStartChallengeNodeCommand(
                    commandOrQuery.userId,
                    commandOrQuery.nodeId,
                    commandOrQuery.conversationId,
                )
            case OpenVisitedChallengeNodeQuery():
                return await self.openVisitedChallengeNodeQueryHandler.handleOpenVisitedChallengeNodeQuery(
                    commandOrQuery.userId,
                    commandOrQuery.nodeId,
                )
