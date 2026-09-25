import pytest

from data_transfer_objects.conversation import Conversation
from exceptions.conversation_not_found_exception import ConversationNotFoundException
from command_handlers.delete_conversation_command_handler import (
    DeleteConversationCommandHandler,
)


@pytest.mark.asyncio
async def test_handleDeleteConversationCommand_deletes(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    unitOfWork.conversationRepository.getConversation.return_value = Conversation(id=9)
    handler = DeleteConversationCommandHandler(unitOfWorkFactory)

    await handler.handleDeleteConversationCommand(9, userId)

    unitOfWork.conversationRepository.deleteConversation.assert_awaited_once_with(
        9,
        userId,
    )


@pytest.mark.asyncio
async def test_handleDeleteConversationCommand_notFound(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    unitOfWork.conversationRepository.getConversation.return_value = None
    handler = DeleteConversationCommandHandler(unitOfWorkFactory)

    with pytest.raises(ConversationNotFoundException):
        await handler.handleDeleteConversationCommand(9, userId)

    unitOfWork.conversationRepository.deleteConversation.assert_not_awaited()
