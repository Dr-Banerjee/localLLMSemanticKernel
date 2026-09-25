from abstractions.i_command import ICommand
from abstractions.i_query import IQuery
from commands.chat_command import ChatCommand
from queries.conversationMessagesQuery import ConversationMessagesQuery
from queries.conversationSummariesQuery import ConversationSummariesQuery
from command_handlers.chat_command_handler import ChatCommandHandler
from query_handlers.conversation_messages_query_handler import ConversationMessagesQueryHandler
from query_handlers.conversation_summaries_query_handler import ConversationSummariesQueryHandler


class Mediator:
    def __init__(
        self,
        chatCommandHandler: ChatCommandHandler,
        conversationSummariesQueryHandler: ConversationSummariesQueryHandler,
        conversationMessagesQueryHandler: ConversationMessagesQueryHandler,
    ) -> None:
        self.chatCommandHandler = chatCommandHandler
        self.conversationSummariesQueryHandler = conversationSummariesQueryHandler
        self.conversationMessagesQueryHandler = conversationMessagesQueryHandler

    async def send(self, commandOrQuery: ICommand | IQuery):
        match commandOrQuery:
            case ChatCommand():
                return await self.chatCommandHandler.handleChatCommand(
                    commandOrQuery.conversationId,
                    commandOrQuery.request,
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
