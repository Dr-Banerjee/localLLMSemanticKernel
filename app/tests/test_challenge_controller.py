from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid7

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from commands.create_challenge_progress_command import CreateChallengeProgressCommand
from commands.update_challenge_progress_command import UpdateChallengeProgressCommand
from controllers.challenge_controller import ChallengeController
from exceptions.challenge_progress_already_exists_exception import (
    ChallengeProgressAlreadyExistsException,
)
from exceptions.challenge_progress_not_found_exception import (
    ChallengeProgressNotFoundException,
)
from models.challenge_progress import ChallengeProgress
from models.user import User
from queries.challenge_progress_query import ChallengeProgressQuery


@pytest.fixture
def currentUser():
    return User(id=uuid7())


@pytest.fixture
def progress(currentUser):
    now = datetime.now(UTC)
    return ChallengeProgress(
        user_id=currentUser.id,
        created_at=now,
        updated_at=now,
        challenge_step=1,
    )


@pytest.fixture
def appClient(currentUser, progress):
    mediator = MagicMock()
    mediator.send = AsyncMock(return_value=progress)
    currentUserDependency = MagicMock()

    async def resolveCurrentUser():
        return currentUser

    currentUserDependency.resolveCurrentUser = resolveCurrentUser
    controller = ChallengeController(mediator, currentUserDependency)
    app = FastAPI()
    app.include_router(controller.router)
    client = TestClient(app)
    return client, mediator, currentUser


def test_createChallengeProgress_success(appClient, currentUser):
    client, mediator, _ = appClient

    response = client.post("/api/challenge", json={"challenge_step": 1})

    assert response.status_code == 200
    assert response.json()["challenge_step"] == 1
    assert response.json()["user_id"] == str(currentUser.id)
    command = mediator.send.await_args.args[0]
    assert isinstance(command, CreateChallengeProgressCommand)
    assert command.userId == currentUser.id
    assert command.challengeStep == 1


def test_createChallengeProgress_alreadyExists(appClient):
    client, mediator, _ = appClient
    mediator.send = AsyncMock(side_effect=ChallengeProgressAlreadyExistsException())

    response = client.post("/api/challenge", json={"challenge_step": 1})

    assert response.status_code == 409
    assert response.json()["detail"] == "Challenge progress already exists"


def test_updateChallengeProgress_success(appClient, currentUser):
    client, mediator, _ = appClient

    response = client.patch("/api/challenge", json={"challenge_step": 2})

    assert response.status_code == 200
    command = mediator.send.await_args.args[0]
    assert isinstance(command, UpdateChallengeProgressCommand)
    assert command.userId == currentUser.id
    assert command.challengeStep == 2


def test_updateChallengeProgress_notFound(appClient):
    client, mediator, _ = appClient
    mediator.send = AsyncMock(side_effect=ChallengeProgressNotFoundException())

    response = client.patch("/api/challenge", json={"challenge_step": 2})

    assert response.status_code == 404
    assert response.json()["detail"] == "Challenge progress not found"


def test_getChallengeProgress_success(appClient, currentUser):
    client, mediator, _ = appClient

    response = client.get("/api/challenge")

    assert response.status_code == 200
    assert response.json()["user_id"] == str(currentUser.id)
    command = mediator.send.await_args.args[0]
    assert isinstance(command, ChallengeProgressQuery)
    assert command.userId == currentUser.id


def test_getChallengeProgress_notFound(appClient):
    client, mediator, _ = appClient
    mediator.send = AsyncMock(side_effect=ChallengeProgressNotFoundException())

    response = client.get("/api/challenge")

    assert response.status_code == 404
    assert response.json()["detail"] == "Challenge progress not found"
