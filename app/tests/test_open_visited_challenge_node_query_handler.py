from datetime import datetime, timezone

import pytest

from data_transfer_objects.conversation import Conversation
from data_transfer_objects.conversation_summary import ConversationSummary
from data_transfer_objects.message import Message
from exceptions.challenge_node_not_found_exception import ChallengeNodeNotFoundException
from exceptions.conversation_not_found_exception import ConversationNotFoundException
from query_handlers.open_visited_challenge_node_query_handler import (
    OpenVisitedChallengeNodeQueryHandler,
)
from utils.challenge_idioms import load_challenge_idioms


def _summary(conversationId: int, initialMessage: str) -> ConversationSummary:
    now = datetime.now(timezone.utc)
    return ConversationSummary(
        id=conversationId,
        createdAt=now,
        updatedAt=now,
        initialMessage=initialMessage,
    )


def _handler(unitOfWorkFactory) -> OpenVisitedChallengeNodeQueryHandler:
    return OpenVisitedChallengeNodeQueryHandler(unitOfWorkFactory)


@pytest.mark.asyncio
async def test_handleOpenVisitedChallengeNodeQuery_returnsMessages(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    idiom = load_challenge_idioms()[1]["idiom"]
    now = datetime.now(timezone.utc)
    unitOfWork.conversationRepository.getConversationSummaries.return_value = [
        _summary(4, "some other saying"),
        _summary(9, idiom),
    ]
    unitOfWork.conversationRepository.getConversation.return_value = Conversation(id=9)
    unitOfWork.conversationRepository.getMessages.return_value = [
        Message(id=1, role="user", content=idiom, created_at=now),
        Message(id=2, role="assistant", content="Meaning:\nhello", created_at=now),
    ]
    handler = _handler(unitOfWorkFactory)

    result = await handler.handleOpenVisitedChallengeNodeQuery(userId, 1)

    assert result.conversationId == 9
    assert [message.role for message in result.messages] == ["user", "assistant"]
    assert result.messages[0].content == idiom
    assert result.messages[1].content == "Meaning:\nhello"
    unitOfWork.conversationRepository.getMessages.assert_awaited_once_with(9, userId)


@pytest.mark.asyncio
async def test_handleOpenVisitedChallengeNodeQuery_searchesNextPage(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    idiom = load_challenge_idioms()[2]["idiom"]
    firstPage = [_summary(index, "other") for index in range(101)]
    unitOfWork.conversationRepository.getConversationSummaries.side_effect = [
        firstPage,
        [_summary(15, idiom)],
    ]
    unitOfWork.conversationRepository.getConversation.return_value = Conversation(id=15)
    unitOfWork.conversationRepository.getMessages.return_value = []
    handler = _handler(unitOfWorkFactory)

    result = await handler.handleOpenVisitedChallengeNodeQuery(userId, 2)

    assert result.conversationId == 15
    assert result.messages == []
    assert unitOfWork.conversationRepository.getConversationSummaries.await_count == 2


@pytest.mark.asyncio
async def test_handleOpenVisitedChallengeNodeQuery_missingConversation(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    unitOfWork.conversationRepository.getConversationSummaries.return_value = []
    handler = _handler(unitOfWorkFactory)

    with pytest.raises(ConversationNotFoundException):
        await handler.handleOpenVisitedChallengeNodeQuery(userId, 1)

    unitOfWork.conversationRepository.getConversation.assert_not_awaited()
    unitOfWork.conversationRepository.getMessages.assert_not_awaited()


@pytest.mark.asyncio
async def test_handleOpenVisitedChallengeNodeQuery_unknownNode(
    unitOfWorkFactory,
    userId,
):
    handler = _handler(unitOfWorkFactory)

    with pytest.raises(ChallengeNodeNotFoundException):
        await handler.handleOpenVisitedChallengeNodeQuery(userId, 999999)
