from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid7

import pytest

from db.models.challenge_progress import ChallengeProgress as ChallengeProgressRecord
from db.repositories.challenge_repository import ChallengeRepository


def _result(scalar=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar
    return result


@pytest.mark.asyncio
async def test_challengeRepository_getChallengeProgress_foundAndMissing():
    session = MagicMock()
    userId = uuid7()
    now = datetime.now(UTC)
    record = ChallengeProgressRecord(user_id=userId, challenge_step=1)
    record.created_at = now
    record.updated_at = now
    session.execute = AsyncMock(
        side_effect=[_result(scalar=record), _result(scalar=None)]
    )
    repository = ChallengeRepository(session)

    found = await repository.getChallengeProgress(userId)
    missing = await repository.getChallengeProgress(uuid7())

    assert found.user_id == userId
    assert found.challenge_step == 1
    assert missing is None


@pytest.mark.asyncio
async def test_challengeRepository_createChallengeProgress():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    userId = uuid7()
    now = datetime.now(UTC)

    async def refresh(record):
        record.created_at = now
        record.updated_at = now

    session.refresh = AsyncMock(side_effect=refresh)
    repository = ChallengeRepository(session)

    created = await repository.createChallengeProgress(userId, 1)

    record = session.add.call_args.args[0]
    assert isinstance(record, ChallengeProgressRecord)
    assert created.user_id == userId
    assert created.challenge_step == 1
    assert created.created_at == now
    session.flush.assert_awaited()


@pytest.mark.asyncio
async def test_challengeRepository_updateChallengeProgress_foundAndMissing():
    session = MagicMock()
    userId = uuid7()
    now = datetime.now(UTC)
    record = ChallengeProgressRecord(user_id=userId, challenge_step=1)
    record.created_at = now
    record.updated_at = now

    async def refresh(updated):
        updated.updated_at = now

    session.refresh = AsyncMock(side_effect=refresh)
    session.flush = AsyncMock()
    session.execute = AsyncMock(
        side_effect=[_result(scalar=record), _result(scalar=None)]
    )
    repository = ChallengeRepository(session)

    updated = await repository.updateChallengeProgress(userId, 3)
    missing = await repository.updateChallengeProgress(userId, 4)

    assert updated.challenge_step == 3
    assert record.challenge_step == 3
    assert missing is None
    session.flush.assert_awaited()
