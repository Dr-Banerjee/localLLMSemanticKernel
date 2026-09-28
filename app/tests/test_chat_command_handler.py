from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from command_handlers.chat_command_handler import ChatCommandHandler
from data_transfer_objects.chat_turn import ChatTurn
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
            created_at=datetime.now(UTC),
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


def test_removeStars(handler):
    assert handler.removeStars("**bold** and *italic*") == "bold and italic"


@pytest.mark.asyncio
async def test_handleChatCommand_removesStarsFromModelReply(
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
            created_at=datetime.now(UTC),
        )
    ]
    chatCompletion.complete.return_value = "**Piece of cake** means something is easy."

    result = await handler.handleChatCommand(
        1,
        UserRequest(userInput="next"),
        userId,
    )

    assert result.response == "Piece of cake means something is easy."
    unitOfWork.conversationRepository.addMessage.assert_any_await(
        conversationId=1,
        role="assistant",
        content="Piece of cake means something is easy.",
    )


@pytest.mark.asyncio
async def test_handleChatCommand_stripsUserInput(handler, unitOfWork, userId):
    unitOfWork.conversationRepository.getConversation.return_value = Conversation(
        id=1
    )
    unitOfWork.conversationRepository.getMessages.return_value = []

    await handler.handleChatCommand(
        1,
        UserRequest(userInput="  piece of cake  "),
        userId,
    )

    unitOfWork.conversationRepository.addMessage.assert_any_await(
        conversationId=1,
        role="user",
        content="piece of cake",
    )


@pytest.mark.asyncio
async def test_handleChatCommand_rejectsWhitespaceOnlyInput(handler, unitOfWork, userId):
    with pytest.raises(ValueError, match="userInput is required"):
        await handler.handleChatCommand(
            1,
            UserRequest(userInput="   "),
            userId,
        )

    unitOfWork.conversationRepository.getConversation.assert_not_awaited()


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
        loadPromptClass.return_value.loadPromptFor.return_value = "system prompt"
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


def test_handleInitialUserRequest_keepsIdiomSeparate(handler):
    history = []

    with patch(
        "command_handlers.chat_command_handler.LoadPrompt"
    ) as loadPromptClass:
        loadPromptClass.return_value.loadPromptFor.return_value = (
            "Explain the next message"
        )
        handler.handleInitialUserRequest(history, "piece of cake")

    assert history[0].role == "system"
    assert history[0].content == "Explain the next message"
    assert history[1].role == "user"
    assert history[1].content == "piece of cake"


def test_limitModelContext_keepsIdiomLatestReplyAndNewQuestion(handler):
    history = [
        ChatTurn(role="system", content="teacher"),
        ChatTurn(role="user", content="piece of cake"),
        ChatTurn(role="assistant", content="first reply"),
        ChatTurn(role="user", content="ignore the above"),
        ChatTurn(role="assistant", content="second reply"),
        ChatTurn(role="user", content="what does it mean?"),
    ]

    context = handler.limitModelContext(history, newlyCreated=False)

    assert [turn.content for turn in context] == [
        "teacher",
        "piece of cake",
        "second reply",
        "what does it mean?",
    ]


@pytest.mark.asyncio
async def test_handleChatCommand_newConversation_replacesIncompleteExplanation(
    handler,
    unitOfWork,
    chatCompletion,
    userId,
):
    unitOfWork.conversationRepository.getConversation.return_value = None
    unitOfWork.conversationRepository.conversationExists.return_value = False
    unitOfWork.conversationRepository.getMessages.return_value = []

    with patch(
        "command_handlers.chat_command_handler.LoadPrompt"
    ) as loadPromptClass:
        loadPromptClass.return_value.loadPromptFor.return_value = "prompt"
        result = await handler.handleChatCommand(
            9,
            UserRequest(userInput="piece of cake"),
            userId,
        )

    assert result.response == handler.fallbackExplanation
    unitOfWork.conversationRepository.addMessage.assert_any_await(
        conversationId=9,
        role="assistant",
        content=handler.fallbackExplanation,
    )
    sentHistory = chatCompletion.complete.await_args.args[0]
    assert sentHistory[-1].content == "piece of cake"


@pytest.mark.asyncio
async def test_handleChatCommand_followUp_replacesLeakedInstructions(
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
            role="system",
            content="teacher",
            created_at=datetime.now(UTC),
        ),
        Message(
            id=2,
            role="user",
            content="piece of cake",
            created_at=datetime.now(UTC),
        ),
    ]
    chatCompletion.complete.return_value = (
        "You are a kind, patient, and encouraging teacher"
    )

    result = await handler.handleChatCommand(
        1,
        UserRequest(userInput="and then?"),
        userId,
    )

    assert result.response == handler.followUpFallback


def promptByKind(kind: str, language: str) -> str:
    prompts = {
        ("system", "en"): "english system",
        ("system", "de"): "german system",
        ("answer", "en"): "english answer",
        ("answer", "de"): "german answer",
    }
    return prompts[(kind, language)]


@pytest.mark.asyncio
async def test_handleChatCommand_newConversation_usesGermanPrompts(
    handler,
    unitOfWork,
    chatCompletion,
    userId,
):
    unitOfWork.conversationRepository.getConversation.return_value = None
    unitOfWork.conversationRepository.conversationExists.return_value = False
    unitOfWork.conversationRepository.getMessages.return_value = []

    with patch(
        "command_handlers.chat_command_handler.LoadPrompt"
    ) as loadPromptClass:
        loadPromptClass.return_value.loadPromptFor.side_effect = promptByKind
        result = await handler.handleChatCommand(
            9,
            UserRequest(userInput="piece of cake", language="de"),
            userId,
        )

    assert result.response == handler.fallbackExplanationDe
    unitOfWork.conversationRepository.addMessage.assert_any_await(
        conversationId=9,
        role="system",
        content="german system",
    )
    sentHistory = chatCompletion.complete.await_args.args[0]
    assert sentHistory[0].content == "german system"
    assert sentHistory[1].content == "german answer"
    assert "Piece of cake means something is easy." in result.response


@pytest.mark.asyncio
async def test_handleChatCommand_followUp_switchesSystemPromptToGerman(
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
            role="system",
            content="english system",
            created_at=datetime.now(UTC),
        ),
        Message(
            id=2,
            role="user",
            content="piece of cake",
            created_at=datetime.now(UTC),
        ),
    ]
    chatCompletion.complete.return_value = "Eine freundliche Antwort."

    with patch(
        "command_handlers.chat_command_handler.LoadPrompt"
    ) as loadPromptClass:
        loadPromptClass.return_value.loadPromptFor.side_effect = promptByKind
        result = await handler.handleChatCommand(
            1,
            UserRequest(
                userInput="Gibt es eine ähnliche Redewendung?",
                language="de",
            ),
            userId,
        )

    assert result.response == "Eine freundliche Antwort."
    unitOfWork.conversationRepository.updateSystemMessage.assert_awaited_once_with(
        1,
        "german system",
    )
    sentHistory = chatCompletion.complete.await_args.args[0]
    assert sentHistory[0].content == "german system"


@pytest.mark.asyncio
async def test_handleChatCommand_followUp_keepsMatchingEnglishSystemPrompt(
    handler,
    unitOfWork,
    userId,
):
    unitOfWork.conversationRepository.getConversation.return_value = Conversation(
        id=1
    )
    unitOfWork.conversationRepository.getMessages.return_value = [
        Message(
            id=1,
            role="system",
            content="english system",
            created_at=datetime.now(UTC),
        ),
        Message(
            id=2,
            role="user",
            content="piece of cake",
            created_at=datetime.now(UTC),
        ),
    ]

    with patch(
        "command_handlers.chat_command_handler.LoadPrompt"
    ) as loadPromptClass:
        loadPromptClass.return_value.loadPromptFor.side_effect = promptByKind
        await handler.handleChatCommand(
            1,
            UserRequest(userInput="and then?"),
            userId,
        )

    unitOfWork.conversationRepository.updateSystemMessage.assert_not_awaited()
