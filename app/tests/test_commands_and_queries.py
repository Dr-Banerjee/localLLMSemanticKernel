from commands.chat_command import ChatCommand
from data_transfer_objects.request import UserRequest
from queries.conversationMessagesQuery import ConversationMessagesQuery
from queries.conversationSummariesQuery import ConversationSummariesQuery
from uuid import uuid7


def test_chatCommand_storesFields():
    request = UserRequest(userInput="hi")
    userId = uuid7()
    command = ChatCommand(4, request, userId)

    assert command.conversationId == 4
    assert command.request is request
    assert command.userId == userId


def test_conversationQueries_storeFields():
    userId = uuid7()
    messagesQuery = ConversationMessagesQuery(8, userId)
    summariesQuery = ConversationSummariesQuery(userId, 3, 15)

    assert messagesQuery.conversationId == 8
    assert messagesQuery.userId == userId
    assert summariesQuery.page == 3
    assert summariesQuery.pageSize == 15
