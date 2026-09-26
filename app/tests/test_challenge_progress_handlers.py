from datetime import UTC, datetime

import pytest

from command_handlers.create_challenge_progress_command_handler import (
    CreateChallengeProgressCommandHandler,
)
from command_handlers.update_challenge_progress_command_handler import (
    UpdateChallengeProgressCommandHandler,
)
from exceptions.challenge_progress_already_exists_exception import (
    ChallengeProgressAlreadyExistsException,
)
from exceptions.challenge_progress_not_found_exception import (
    ChallengeProgressNotFoundException,
)
from models.challenge_progress import ChallengeProgress
from query_handlers.challenge_progress_query_handler import ChallengeProgressQueryHandler


def _progress(userId, challengeStep: int) -> ChallengeProgress:
    now = datetime.now(UTC)
    return ChallengeProgress(
        user_id=userId,
        created_at=now,
        updated_at=now,
        challenge_step=challengeStep,
    )


@pytest.mark.asyncio
async def test_handleCreateChallengeProgressCommand_creates(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    created = _progress(userId, 1)
    unitOfWork.challengeRepository.getChallengeProgress.return_value = None
    unitOfWork.challengeRepository.createChallengeProgress.return_value = created
    handler = CreateChallengeProgressCommandHandler(unitOfWorkFactory)

    result = await handler.handleCreateChallengeProgressCommand(userId, 1)

    assert result is created
    unitOfWork.challengeRepository.createChallengeProgress.assert_awaited_once_with(
        userId,
        1,
    )


@pytest.mark.asyncio
async def test_handleCreateChallengeProgressCommand_alreadyExists(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    unitOfWork.challengeRepository.getChallengeProgress.return_value = _progress(
        userId,
        1,
    )
    handler = CreateChallengeProgressCommandHandler(unitOfWorkFactory)

    with pytest.raises(ChallengeProgressAlreadyExistsException):
        await handler.handleCreateChallengeProgressCommand(userId, 1)

    unitOfWork.challengeRepository.createChallengeProgress.assert_not_awaited()


@pytest.mark.asyncio
async def test_handleUpdateChallengeProgressCommand_updates(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    updated = _progress(userId, 2)
    unitOfWork.challengeRepository.updateChallengeProgress.return_value = updated
    handler = UpdateChallengeProgressCommandHandler(unitOfWorkFactory)

    result = await handler.handleUpdateChallengeProgressCommand(userId, 2)

    assert result.challenge_step == 2
    unitOfWork.challengeRepository.updateChallengeProgress.assert_awaited_once_with(
        userId,
        2,
    )


@pytest.mark.asyncio
async def test_handleUpdateChallengeProgressCommand_notFound(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    unitOfWork.challengeRepository.updateChallengeProgress.return_value = None
    handler = UpdateChallengeProgressCommandHandler(unitOfWorkFactory)

    with pytest.raises(ChallengeProgressNotFoundException):
        await handler.handleUpdateChallengeProgressCommand(userId, 2)


@pytest.mark.asyncio
async def test_handleChallengeProgressQuery_returnsProgress(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    progress = _progress(userId, 1)
    unitOfWork.challengeRepository.getChallengeProgress.return_value = progress
    handler = ChallengeProgressQueryHandler(unitOfWorkFactory)

    result = await handler.handleChallengeProgressQuery(userId)

    assert result is progress


@pytest.mark.asyncio
async def test_handleChallengeProgressQuery_notFound(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    unitOfWork.challengeRepository.getChallengeProgress.return_value = None
    handler = ChallengeProgressQueryHandler(unitOfWorkFactory)

    with pytest.raises(ChallengeProgressNotFoundException):
        await handler.handleChallengeProgressQuery(userId)
