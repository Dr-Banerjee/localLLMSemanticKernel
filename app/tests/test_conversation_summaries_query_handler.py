import pytest

from query_handlers.conversation_summaries_query_handler import (
    ConversationSummariesQueryHandler,
)


@pytest.mark.asyncio
async def test_handleConversationSummariesQuery_paginates(
    unitOfWorkFactory,
    unitOfWork,
    userId,
    conversationSummary,
):
    extra = conversationSummary.model_copy(update={"id": 2})
    unitOfWork.conversationRepository.getConversationSummaries.return_value = [
        conversationSummary,
        extra,
    ]
    handler = ConversationSummariesQueryHandler(unitOfWorkFactory)

    result = await handler.handleConversationSummariesQuery(userId, 1, 1)

    assert result.page == 1
    assert result.pageSize == 1
    assert result.hasNextPage is True
    assert len(result.items) == 1
    assert result.items[0].id == conversationSummary.id


@pytest.mark.asyncio
async def test_handleConversationSummariesQuery_withoutNextPage(
    unitOfWorkFactory,
    unitOfWork,
    userId,
    conversationSummary,
):
    unitOfWork.conversationRepository.getConversationSummaries.return_value = [
        conversationSummary
    ]
    handler = ConversationSummariesQueryHandler(unitOfWorkFactory)

    result = await handler.handleConversationSummariesQuery(userId, 1, 20)

    assert result.hasNextPage is False
    assert len(result.items) == 1
