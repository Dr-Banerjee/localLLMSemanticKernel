from unittest.mock import AsyncMock, MagicMock

import pytest

from db.unit_of_work import UnitOfWork
from db.unit_of_work_factory import UnitOfWorkFactory


@pytest.mark.asyncio
async def test_unitOfWork_commitsOnSuccess():
    database = MagicMock()
    session = MagicMock()
    session.rollback = AsyncMock()
    session.commit = AsyncMock()
    session.close = AsyncMock()
    database.createSession.return_value = session

    async with UnitOfWork(database) as unitOfWork:
        assert unitOfWork.session is session

    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()
    session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_unitOfWork_rollbacksOnError():
    database = MagicMock()
    session = MagicMock()
    session.rollback = AsyncMock()
    session.commit = AsyncMock()
    session.close = AsyncMock()
    database.createSession.return_value = session

    with pytest.raises(RuntimeError):
        async with UnitOfWork(database):
            raise RuntimeError("boom")

    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()
    session.close.assert_awaited_once()


def test_unitOfWorkFactory_create_returnsUnitOfWork():
    database = MagicMock()
    session = MagicMock()
    database.createSession.return_value = session
    factory = UnitOfWorkFactory(database)

    unitOfWork = factory.create()

    assert isinstance(unitOfWork, UnitOfWork)
    assert unitOfWork.session is session
