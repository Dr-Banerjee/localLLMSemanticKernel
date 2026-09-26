from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid7

import pytest

from data_transfer_objects.conversation_summary import ConversationSummary
from data_transfer_objects.message import Message
from data_transfer_objects.request import UserRequest
from data_transfer_objects.session import Session
from models.user import User


@pytest.fixture
def userId():
    return uuid7()


@pytest.fixture
def user(userId):
    return User(id=userId)


@pytest.fixture
def userRequest():
    return UserRequest(userInput="break the ice")


@pytest.fixture
def message():
    return Message(
        id=1,
        role="user",
        content="hello",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sessionDto(userId):
    return Session(user_id=userId)


@pytest.fixture
def conversationSummary():
    return ConversationSummary(
        id=1,
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
        initialMessage="hello",
    )


@pytest.fixture
def unitOfWork():
    uow = MagicMock()
    uow.conversationRepository = MagicMock()
    uow.sessionRepository = MagicMock()
    uow.userRepository = MagicMock()
    uow.conversationRepository.getConversation = AsyncMock()
    uow.conversationRepository.conversationExists = AsyncMock()
    uow.conversationRepository.createConversation = AsyncMock()
    uow.conversationRepository.getMessages = AsyncMock()
    uow.conversationRepository.addMessage = AsyncMock()
    uow.conversationRepository.getConversationSummaries = AsyncMock()
    uow.conversationRepository.deleteConversation = AsyncMock()
    uow.sessionRepository.getValidSession = AsyncMock()
    uow.sessionRepository.createSession = AsyncMock()
    uow.userRepository.createUser = AsyncMock()
    uow.userRepository.getUser = AsyncMock()
    uow.challengeRepository = MagicMock()
    uow.challengeRepository.getChallengeProgress = AsyncMock()
    uow.challengeRepository.createChallengeProgress = AsyncMock()
    uow.challengeRepository.updateChallengeProgress = AsyncMock()
    return uow


@pytest.fixture
def unitOfWorkFactory(unitOfWork):
    factory = MagicMock()
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=unitOfWork)
    context.__aexit__ = AsyncMock(return_value=None)
    factory.create.return_value = context
    return factory
