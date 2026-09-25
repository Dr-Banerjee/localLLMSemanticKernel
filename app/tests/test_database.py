from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from db.database import Database


def test_database_createSession_usesSessionFactory():
    with (
        patch("db.database.create_async_engine") as createEngine,
        patch("db.database.async_sessionmaker") as sessionMaker,
    ):
        engine = MagicMock()
        createEngine.return_value = engine
        sessionFactory = MagicMock(return_value="session")
        sessionMaker.return_value = sessionFactory

        database = Database("postgresql+asyncpg://user:pass@localhost/db")
        session = database.createSession()

        assert session == "session"
        createEngine.assert_called_once()
        sessionFactory.assert_called_once()


@pytest.mark.asyncio
async def test_database_dispose():
    with (
        patch("db.database.create_async_engine") as createEngine,
        patch("db.database.async_sessionmaker"),
    ):
        engine = MagicMock()
        engine.dispose = AsyncMock()
        createEngine.return_value = engine
        database = Database("postgresql+asyncpg://user:pass@localhost/db")

        await database.dispose()

        engine.dispose.assert_awaited_once()
