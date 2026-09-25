from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from command_handlers.chat_command_handler import ChatCommandHandler
from data_transfer_objects.conversation import Conversation
from data_transfer_objects.message import Message
from data_transfer_objects.request import UserRequest
from exceptions.conversation_forbidden_exception import ConversationForbiddenException
from models.conversation_course import ConversationCourse


@pytest.fixture
def chatCompletion():
    completion = MagicMock()
    completion.complete = AsyncMock(return_value="assistant reply")
    return completion


@pytest.fixture
def handler(unitOfWorkFactory, chatCompletion):
    return ChatCommandHandler(unitOfWorkFactory, chatCompletion)


@pytest.mark.asyncio
async def test_handleChatCommand_existingConversation(
    handler,
    unitOfWork,
    chatCompletion,
    userId,
):
    unitOfWork.conversationRepository.getConversation.return_value = Conversation(
        id=1
    )
    unitOfWork.conversationRepository.getMessages.return_value = [
        Message(
            id=1,
            role="user",
            content="hi",
            created_at=datetime.now(timezone.utc),
        )
    ]

    result = await handler.handleChatCommand(
        1,
        UserRequest(userInput="next"),
        userId,
    )

    assert result.response == "assistant reply"
    chatCompletion.complete.assert_awaited_once()
    assert unitOfWork.conversationRepository.addMessage.await_count == 2


@pytest.mark.asyncio
async def test_getOrCreateConversationCourse_forbidden(
    handler,
    unitOfWork,
    userId,
):
    unitOfWork.conversationRepository.getConversation.return_value = None
    unitOfWork.conversationRepository.conversationExists.return_value = True

    with pytest.raises(ConversationForbiddenException):
        await handler.getOrCreateConversationCourse(1, userId)


@pytest.mark.asyncio
async def test_getOrCreateConversationCourse_createsNew(
    handler,
    unitOfWork,
    userId,
):
    unitOfWork.conversationRepository.getConversation.return_value = None
    unitOfWork.conversationRepository.conversationExists.return_value = False
    unitOfWork.conversationRepository.getMessages.return_value = []

    with patch(
        "command_handlers.chat_command_handler.LoadPrompt"
    ) as loadPromptClass:
        loadPromptClass.return_value.loadPrompt.return_value = "system prompt"
        course = await handler.getOrCreateConversationCourse(5, userId)

    assert course.newlyCreated is True
    assert course.conversationId == 5
    assert course.chatHistory[0].role == "system"
    assert course.chatHistory[0].content == "system prompt"
    unitOfWork.conversationRepository.createConversation.assert_awaited_once_with(
        5,
        userId,
    )


@pytest.mark.asyncio
async def test_addUserInput_forExistingConversation(
    handler,
    unitOfWork,
    userId,
):
    course = ConversationCourse(
        conversationId=3,
        chatHistory=[],
        newlyCreated=False,
    )

    result = await handler.addUserInputToConversationCourse(course, "hello")

    assert result[-1].role == "user"
    assert result[-1].content == "hello"
    unitOfWork.conversationRepository.addMessage.assert_awaited_once_with(
        conversationId=3,
        role="user",
        content="hello",
    )


def test_handleInitialUserRequest_replacesPlaceholder(handler):
    history = []

    with patch(
        "command_handlers.chat_command_handler.LoadPrompt"
    ) as loadPromptClass:
        loadPromptClass.return_value.loadPrompt.return_value = (
            "Explain {{$user_input}}"
        )
        handler.handleInitialUserRequest(history, "piece of cake")

    assert history[0].role == "user"
    assert history[0].content == "Explain piece of cake"
