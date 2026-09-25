from unittest.mock import AsyncMock, MagicMock
from uuid import uuid7

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from controllers.conversations_controller import ConversationsController
from data_transfer_objects.response import ResponseToUserRequest
from exceptions.conversation_forbidden_exception import ConversationForbiddenException
from exceptions.conversation_not_found_exception import ConversationNotFoundException
from models.user import User


@pytest.fixture
def currentUser():
    return User(id=uuid7())


@pytest.fixture
def appClient(currentUser):
    mediator = MagicMock()
    mediator.send = AsyncMock(
        return_value=ResponseToUserRequest(response="assistant")
    )
    currentUserDependency = MagicMock()

    async def resolveCurrentUser():
        return currentUser

    currentUserDependency.resolveCurrentUser = resolveCurrentUser
    controller = ConversationsController(mediator, currentUserDependency)
    app = FastAPI()
    app.include_router(controller.router)
    client = TestClient(app)
    return client, mediator, currentUser


def test_sendMessage_success(appClient, currentUser):
    client, mediator, _ = appClient

    response = client.post(
        "/api/conversations/11/messages",
        json={"userInput": "hello"},
    )

    assert response.status_code == 200
    assert response.json()["response"] == "assistant"
    mediator.send.assert_awaited()


def test_sendMessage_forbidden(appClient):
    client, mediator, _ = appClient
    mediator.send = AsyncMock(side_effect=ConversationForbiddenException())

    response = client.post(
        "/api/conversations/11/messages",
        json={"userInput": "hello"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Conversation does not belong to the current user"
    )


def test_getConversationSummaries(appClient, currentUser):
    client, mediator, _ = appClient
    mediator.send = AsyncMock(
        return_value={
            "items": [],
            "page": 1,
            "pageSize": 20,
            "hasNextPage": False,
        }
    )

    response = client.get("/api/conversations/summaries?page=1&pageSize=20")

    assert response.status_code == 200
    mediator.send.assert_awaited()


def test_deleteConversation_success(appClient):
    client, mediator, _ = appClient
    mediator.send = AsyncMock(return_value=None)

    response = client.delete("/api/conversations/11")

    assert response.status_code == 204
    mediator.send.assert_awaited()


def test_deleteConversation_notFound(appClient):
    client, mediator, _ = appClient
    mediator.send = AsyncMock(side_effect=ConversationNotFoundException())

    response = client.delete("/api/conversations/11")

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found"


def test_getConversationMessages_notFound(appClient):
    client, mediator, _ = appClient
    mediator.send = AsyncMock(side_effect=ConversationNotFoundException())

    response = client.get("/api/conversations/11/messages")

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found"
