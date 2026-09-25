from unittest.mock import AsyncMock, MagicMock

import pytest

from commands.chat_command import ChatCommand
from commands.delete_conversation_command import DeleteConversationCommand
from data_transfer_objects.request import UserRequest
from data_transfer_objects.response import ResponseToUserRequest
from queries.conversationMessagesQuery import ConversationMessagesQuery
from queries.conversationSummariesQuery import ConversationSummariesQuery
from utils.mediator import Mediator


@pytest.fixture
def mediator():
    chatHandler = MagicMock()
    chatHandler.handleChatCommand = AsyncMock(
        return_value=ResponseToUserRequest(response="ok")
    )
    messagesHandler = MagicMock()
    messagesHandler.handleConversationMessagesQuery = AsyncMock(return_value=[])
    summariesHandler = MagicMock()
    summariesHandler.handleConversationSummariesQuery = AsyncMock(
        return_value="summaries"
    )
    deleteHandler = MagicMock()
    deleteHandler.handleDeleteConversationCommand = AsyncMock(return_value=None)
    return Mediator(chatHandler, summariesHandler, messagesHandler, deleteHandler)


@pytest.mark.asyncio
async def test_send_routesChatCommand(mediator, userRequest, userId):
    command = ChatCommand(1, userRequest, userId)

    result = await mediator.send(command)

    assert result.response == "ok"
    mediator.chatCommandHandler.handleChatCommand.assert_awaited_once_with(
        1,
        userRequest,
        userId,
    )


@pytest.mark.asyncio
async def test_send_routesConversationMessagesQuery(mediator, userId):
    query = ConversationMessagesQuery(7, userId)

    result = await mediator.send(query)

    assert result == []
    mediator.conversationMessagesQueryHandler.handleConversationMessagesQuery.assert_awaited_once_with(
        7,
        userId,
    )


@pytest.mark.asyncio
async def test_send_routesConversationSummariesQuery(mediator, userId):
    query = ConversationSummariesQuery(userId, 2, 10)

    result = await mediator.send(query)

    assert result == "summaries"
    mediator.conversationSummariesQueryHandler.handleConversationSummariesQuery.assert_awaited_once_with(
        userId,
        2,
        10,
    )


@pytest.mark.asyncio
async def test_send_routesDeleteConversationCommand(mediator, userId):
    command = DeleteConversationCommand(4, userId)

    result = await mediator.send(command)

    assert result is None
    mediator.deleteConversationCommandHandler.handleDeleteConversationCommand.assert_awaited_once_with(
        4,
        userId,
    )


@pytest.mark.asyncio
async def test_send_returnsNoneForUnknownType(mediator):
    result = await mediator.send(object())

    assert result is None
