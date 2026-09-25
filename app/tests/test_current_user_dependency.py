from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from auth.current_user_dependency import CurrentUserDependency
from auth.session_token_service import SessionTokenService
from exceptions.invalid_session_exception import InvalidSessionException
from exceptions.user_not_found_exception import UserNotFoundException


@pytest.fixture
def settings():
    value = MagicMock()
    value.sessionCookieName = "session"
    return value


@pytest.fixture
def dependency(settings, user):
    currentUserService = MagicMock()
    currentUserService.resolveCurrentUser = AsyncMock(return_value=user)
    return CurrentUserDependency(
        currentUserService,
        SessionTokenService(),
        settings,
    )


@pytest.mark.asyncio
async def test_resolveCurrentUser_readsCookieAndReturnsUser(dependency, user):
    request = MagicMock()
    request.cookies.get.return_value = "raw-token"

    result = await dependency.resolveCurrentUser(request)

    assert result == user
    request.cookies.get.assert_called_once_with("session")
    dependency.currentUserService.resolveCurrentUser.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolveCurrentUser_requiresCookie(dependency):
    request = MagicMock()
    request.cookies.get.return_value = None

    with pytest.raises(HTTPException) as raised:
        await dependency.resolveCurrentUser(request)

    assert raised.value.status_code == 401
    assert raised.value.detail == "Session required"


@pytest.mark.asyncio
async def test_resolveCurrentUser_mapsInvalidSession(dependency):
    request = MagicMock()
    request.cookies.get.return_value = "raw-token"
    dependency.currentUserService.resolveCurrentUser = AsyncMock(
        side_effect=InvalidSessionException("Invalid or expired session")
    )

    with pytest.raises(HTTPException) as raised:
        await dependency.resolveCurrentUser(request)

    assert raised.value.status_code == 401
    assert raised.value.detail == "Invalid or expired session"


@pytest.mark.asyncio
async def test_resolveCurrentUser_mapsUserNotFound(dependency):
    request = MagicMock()
    request.cookies.get.return_value = "raw-token"
    dependency.currentUserService.resolveCurrentUser = AsyncMock(
        side_effect=UserNotFoundException("User not found")
    )

    with pytest.raises(HTTPException) as raised:
        await dependency.resolveCurrentUser(request)

    assert raised.value.status_code == 401
    assert raised.value.detail == "User not found"
