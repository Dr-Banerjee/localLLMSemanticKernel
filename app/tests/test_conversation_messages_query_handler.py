from datetime import datetime, timezone

import pytest

from data_transfer_objects.conversation import Conversation
from data_transfer_objects.message import Message
from exceptions.conversation_not_found_exception import ConversationNotFoundException
from query_handlers.conversation_messages_query_handler import (
    ConversationMessagesQueryHandler,
)


@pytest.mark.asyncio
async def test_handleConversationMessagesQuery_returnsMessages(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    unitOfWork.conversationRepository.getConversation.return_value = Conversation(
        id=9
    )
    unitOfWork.conversationRepository.getMessages.return_value = [
        Message(
            id=1,
            role="user",
            content="hi",
            created_at=datetime.now(timezone.utc),
        )
    ]
    handler = ConversationMessagesQueryHandler(unitOfWorkFactory)

    result = await handler.handleConversationMessagesQuery(9, userId)

    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].role == "user"
    assert result[0].content == "hi"


@pytest.mark.asyncio
async def test_handleConversationMessagesQuery_notFound(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    unitOfWork.conversationRepository.getConversation.return_value = None
    handler = ConversationMessagesQueryHandler(unitOfWorkFactory)

    with pytest.raises(ConversationNotFoundException):
        await handler.handleConversationMessagesQuery(9, userId)
