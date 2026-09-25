from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid7

import pytest

from db.models.conversation import Conversation as ConversationRecord
from db.models.message import Message as MessageRecord
from db.models.session import Session as SessionRecord
from db.models.user import User as UserRecord
from db.repositories.conversation_repository import ConversationRepository
from db.repositories.session_repository import SessionRepository
from db.repositories.user_repository import UserRepository


def _result(scalar=None, scalars_all=None, mappings_all=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar
    scalars = MagicMock()
    scalars.all.return_value = scalars_all or []
    result.scalars.return_value = scalars
    mappings = MagicMock()
    mappings.all.return_value = mappings_all or []
    result.mappings.return_value = mappings
    return result


@pytest.mark.asyncio
async def test_userRepository_createUser():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()

    async def refresh(record):
        record.id = uuid7()

    session.refresh = AsyncMock(side_effect=refresh)
    repository = UserRepository(session)

    created = await repository.createUser()

    assert created.id is not None
    session.add.assert_called_once()
    assert isinstance(session.add.call_args.args[0], UserRecord)


@pytest.mark.asyncio
async def test_userRepository_getUser_foundAndMissing():
    session = MagicMock()
    userId = uuid7()
    record = UserRecord()
    record.id = userId
    session.execute = AsyncMock(
        side_effect=[_result(scalar=record), _result(scalar=None)]
    )
    repository = UserRepository(session)

    found = await repository.getUser(userId)
    missing = await repository.getUser(uuid7())

    assert found.id == userId
    assert missing is None


@pytest.mark.asyncio
async def test_sessionRepository_createAndGet():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    userId = uuid7()
    expiresAt = datetime.now(timezone.utc)
    repository = SessionRepository(session)

    created = await repository.createSession(userId, "hash", expiresAt)

    record = session.add.call_args.args[0]
    assert isinstance(record, SessionRecord)
    assert created.user_id == userId

    session.execute = AsyncMock(return_value=_result(scalar=record))
    found = await repository.getValidSession("hash")
    assert found.user_id == userId


@pytest.mark.asyncio
async def test_sessionRepository_getValidSession_none():
    session = MagicMock()
    session.execute = AsyncMock(return_value=_result(scalar=None))
    repository = SessionRepository(session)

    assert await repository.getValidSession("hash") is None


@pytest.mark.asyncio
async def test_conversationRepository_crudPaths():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    userId = uuid7()
    now = datetime.now(timezone.utc)

    async def refresh(record):
        if getattr(record, "id", None) is None and hasattr(record, "role"):
            record.id = 1
            record.created_at = now

    session.refresh = AsyncMock(side_effect=refresh)

    conversationRecord = ConversationRecord(id=5, user_id=userId)
    conversationRecord.updated_at = now
    messageRecord = MessageRecord(
        conversation_id=5,
        role="user",
        content="hi",
    )
    messageRecord.id = 1
    messageRecord.created_at = now
    session.get = AsyncMock(return_value=conversationRecord)
    session.execute = AsyncMock(
        side_effect=[
            _result(scalar=conversationRecord),
            _result(scalar=None),
            _result(scalars_all=[messageRecord]),
            _result(scalar=conversationRecord),
            _result(scalar=None),
            _result(
                mappings_all=[
                    {
                        "id": 5,
                        "createdAt": now,
                        "updatedAt": now,
                        "initialMessage": "hi",
                    }
                ]
            ),
        ]
    )
    repository = ConversationRepository(session)

    found = await repository.getConversation(5, userId)
    missing = await repository.getConversation(6, userId)
    created = await repository.createConversation(7, userId)
    added = await repository.addMessage(5, "user", "hi")
    messages = await repository.getMessages(5, userId)
    exists = await repository.conversationExists(5)
    missingExists = await repository.conversationExists(99)
    summaries = await repository.getConversationSummaries(userId, 1, 20)

    assert found.id == 5
    assert missing is None
    assert created.id == 7
    assert added.content == "hi"
    assert messages[0].role == "user"
    assert exists is True
    assert missingExists is False
    assert summaries[0].id == 5


@pytest.mark.asyncio
async def test_conversationRepository_deleteConversation():
    session = MagicMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    repository = ConversationRepository(session)
    userId = uuid7()

    await repository.deleteConversation(5, userId)

    session.execute.assert_awaited()
    session.flush.assert_awaited()
