from commands.chat_command import ChatCommand
from commands.create_challenge_progress_command import CreateChallengeProgressCommand
from commands.delete_conversation_command import DeleteConversationCommand
from commands.update_challenge_progress_command import UpdateChallengeProgressCommand
from data_transfer_objects.request import UserRequest
from queries.challenge_progress_query import ChallengeProgressQuery
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


def test_deleteConversationCommand_storesFields():
    userId = uuid7()
    command = DeleteConversationCommand(6, userId)

    assert command.conversationId == 6
    assert command.userId == userId


def test_conversationQueries_storeFields():
    userId = uuid7()
    messagesQuery = ConversationMessagesQuery(8, userId)
    summariesQuery = ConversationSummariesQuery(userId, 3, 15)

    assert messagesQuery.conversationId == 8
    assert messagesQuery.userId == userId
    assert summariesQuery.page == 3
    assert summariesQuery.pageSize == 15


def test_challengeProgressCommandAndQuery_storeFields():
    userId = uuid7()
    createCommand = CreateChallengeProgressCommand(userId, 1)
    updateCommand = UpdateChallengeProgressCommand(userId, 2)
    query = ChallengeProgressQuery(userId)

    assert createCommand.userId == userId
    assert createCommand.challengeStep == 1
    assert updateCommand.challengeStep == 2
    assert query.userId == userId
