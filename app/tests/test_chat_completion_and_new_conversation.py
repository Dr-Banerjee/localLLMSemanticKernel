from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from data_transfer_objects.chat_turn import ChatTurn
from kernel.semantic_kernel_chat_completion import SemanticKernelChatCompletion
from models.conversation_course import ConversationCourse


@pytest.mark.asyncio
async def test_addUserInput_forNewConversation_usesInitialPrompt(
    unitOfWorkFactory,
    unitOfWork,
):
    from command_handlers.chat_command_handler import ChatCommandHandler

    chatCompletion = MagicMock()
    handler = ChatCommandHandler(unitOfWorkFactory, chatCompletion)
    course = ConversationCourse(
        conversationId=3,
        chatHistory=[],
        newlyCreated=True,
    )

    with patch(
        "command_handlers.chat_command_handler.LoadPrompt"
    ) as loadPromptClass:
        loadPromptClass.return_value.loadPrompt.return_value = (
            "Explain {{$user_input}}"
        )
        result = await handler.addUserInputToConversationCourse(
            course,
            "break the ice",
        )

    assert result[-1].content == "Explain break the ice"
    unitOfWork.conversationRepository.addMessage.assert_awaited_once()


@pytest.mark.asyncio
async def test_semanticKernelChatCompletion_complete():
    fakeHistory = MagicMock()
    chatService = MagicMock()
    chatService.get_chat_message_content = AsyncMock(return_value="done")

    with (
        patch(
            "kernel.semantic_kernel_chat_completion.createKernel"
        ) as createKernel,
        patch(
            "kernel.semantic_kernel_chat_completion.ChatHistory",
            return_value=fakeHistory,
        ),
        patch(
            "kernel.semantic_kernel_chat_completion.OllamaChatPromptExecutionSettings"
        ),
        patch(
            "kernel.semantic_kernel_chat_completion.FunctionChoiceBehavior"
        ),
    ):
        kernel = MagicMock()
        kernel.get_service.return_value = chatService
        createKernel.return_value = kernel
        completion = SemanticKernelChatCompletion()

        result = await completion.complete(
            [
                ChatTurn(role="system", content="s"),
                ChatTurn(role="user", content="u"),
                ChatTurn(role="assistant", content="a"),
            ]
        )

    assert result == "done"
    fakeHistory.add_system_message.assert_called_once_with("s")
    fakeHistory.add_user_message.assert_called_once_with("u")
    fakeHistory.add_assistant_message.assert_called_once_with("a")
    chatService.get_chat_message_content.assert_awaited_once()
