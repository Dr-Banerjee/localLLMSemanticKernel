from unittest.mock import AsyncMock, MagicMock
from uuid import uuid7

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from controllers.sessions_controller import SessionsController
from models.user import User


@pytest.fixture
def settings():
    value = MagicMock()
    value.sessionCookieName = "session"
    value.sessionCookieSecure = False
    value.sessionCookieSameSite = "lax"
    value.anonymousSessionLifetimeDays = 30
    return value


@pytest.fixture
def sessionsApp(settings):
    anonymousSessionService = MagicMock()
    anonymousSessionService.createSession = AsyncMock(return_value="token-value")
    currentUser = User(id=uuid7())
    currentUserDependency = MagicMock()

    async def resolveCurrentUser():
        return currentUser

    currentUserDependency.resolveCurrentUser = resolveCurrentUser
    controller = SessionsController(
        anonymousSessionService,
        currentUserDependency,
        settings,
    )
    app = FastAPI()
    app.include_router(controller.router)
    return TestClient(app), anonymousSessionService, currentUser


def test_createSession_setsCookie(sessionsApp):
    client, anonymousSessionService, _ = sessionsApp

    response = client.post("/api/sessions/session")

    assert response.status_code == 200
    assert response.json() == {"message": "Session created"}
    assert response.cookies["session"] == "token-value"
    anonymousSessionService.createSession.assert_awaited_once()


def test_getCurrentUser(sessionsApp):
    client, _, currentUser = sessionsApp

    response = client.get("/api/sessions/me")

    assert response.status_code == 200
    assert response.json() == {"id": str(currentUser.id)}
