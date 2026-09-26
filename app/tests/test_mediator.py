from unittest.mock import AsyncMock, MagicMock

import pytest

from commands.chat_command import ChatCommand
from commands.create_challenge_progress_command import CreateChallengeProgressCommand
from commands.delete_conversation_command import DeleteConversationCommand
from commands.start_challenge_node_command import StartChallengeNodeCommand
from commands.update_challenge_progress_command import UpdateChallengeProgressCommand
from data_transfer_objects.request import UserRequest
from data_transfer_objects.response import ResponseToUserRequest
from queries.challenge_progress_query import ChallengeProgressQuery
from queries.open_visited_challenge_node_query import OpenVisitedChallengeNodeQuery
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
    createChallengeHandler = MagicMock()
    createChallengeHandler.handleCreateChallengeProgressCommand = AsyncMock(
        return_value="created"
    )
    updateChallengeHandler = MagicMock()
    updateChallengeHandler.handleUpdateChallengeProgressCommand = AsyncMock(
        return_value="updated"
    )
    challengeProgressHandler = MagicMock()
    challengeProgressHandler.handleChallengeProgressQuery = AsyncMock(
        return_value="progress"
    )
    startNodeHandler = MagicMock()
    startNodeHandler.handleStartChallengeNodeCommand = AsyncMock(
        return_value="conversation"
    )
    visitedNodeHandler = MagicMock()
    visitedNodeHandler.handleOpenVisitedChallengeNodeQuery = AsyncMock(
        return_value="visited"
    )
    return Mediator(
        chatHandler,
        summariesHandler,
        messagesHandler,
        deleteHandler,
        createChallengeHandler,
        updateChallengeHandler,
        challengeProgressHandler,
        startNodeHandler,
        visitedNodeHandler,
    )


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
async def test_send_routesCreateChallengeProgressCommand(mediator, userId):
    command = CreateChallengeProgressCommand(userId, 1)

    result = await mediator.send(command)

    assert result == "created"
    mediator.createChallengeProgressCommandHandler.handleCreateChallengeProgressCommand.assert_awaited_once_with(
        userId,
        1,
    )


@pytest.mark.asyncio
async def test_send_routesUpdateChallengeProgressCommand(mediator, userId):
    command = UpdateChallengeProgressCommand(userId, 2)

    result = await mediator.send(command)

    assert result == "updated"
    mediator.updateChallengeProgressCommandHandler.handleUpdateChallengeProgressCommand.assert_awaited_once_with(
        userId,
        2,
    )


@pytest.mark.asyncio
async def test_send_routesChallengeProgressQuery(mediator, userId):
    query = ChallengeProgressQuery(userId)

    result = await mediator.send(query)

    assert result == "progress"
    mediator.challengeProgressQueryHandler.handleChallengeProgressQuery.assert_awaited_once_with(
        userId,
    )


@pytest.mark.asyncio
async def test_send_routesStartChallengeNodeCommand(mediator, userId):
    command = StartChallengeNodeCommand(userId, 1)

    result = await mediator.send(command)

    assert result == "conversation"
    mediator.startChallengeNodeCommandHandler.handleStartChallengeNodeCommand.assert_awaited_once_with(
        userId,
        1,
    )


@pytest.mark.asyncio
async def test_send_routesOpenVisitedChallengeNodeQuery(mediator, userId):
    query = OpenVisitedChallengeNodeQuery(userId, 3)

    result = await mediator.send(query)

    assert result == "visited"
    mediator.openVisitedChallengeNodeQueryHandler.handleOpenVisitedChallengeNodeQuery.assert_awaited_once_with(
        userId,
        3,
    )


@pytest.mark.asyncio
async def test_send_returnsNoneForUnknownType(mediator):
    result = await mediator.send(object())

    assert result is None
