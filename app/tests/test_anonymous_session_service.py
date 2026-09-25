from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from auth.anonymous_session_service import AnonymousSessionService
from auth.session_token_service import SessionTokenService


@pytest.mark.asyncio
async def test_createSession_persistsUserAndSession(
    unitOfWorkFactory,
    unitOfWork,
    user,
):
    settings = MagicMock()
    settings.anonymousSessionLifetimeDays = 30
    tokenService = MagicMock(spec=SessionTokenService)
    tokenService.generateToken.return_value = "plain-token"
    tokenService.hashToken.return_value = "hashed-token"
    unitOfWork.userRepository.createUser.return_value = user

    service = AnonymousSessionService(
        unitOfWorkFactory,
        tokenService,
        settings,
    )

    before = datetime.now(timezone.utc)
    result = await service.createSession()
    after = datetime.now(timezone.utc)

    assert result == "plain-token"
    unitOfWork.userRepository.createUser.assert_awaited_once()
    unitOfWork.sessionRepository.createSession.assert_awaited_once()
    kwargs = unitOfWork.sessionRepository.createSession.await_args.kwargs
    assert kwargs["userId"] == user.id
    assert kwargs["tokenHash"] == "hashed-token"
    assert before + timedelta(days=30) <= kwargs["expiresAt"] <= after + timedelta(days=30)
