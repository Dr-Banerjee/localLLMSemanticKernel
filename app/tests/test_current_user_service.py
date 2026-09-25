import pytest

from auth.current_user_service import CurrentUserService
from exceptions.invalid_session_exception import InvalidSessionException
from exceptions.user_not_found_exception import UserNotFoundException


@pytest.mark.asyncio
async def test_resolveCurrentUser_returnsUser(
    unitOfWorkFactory,
    unitOfWork,
    user,
    sessionDto,
):
    unitOfWork.sessionRepository.getValidSession.return_value = sessionDto
    unitOfWork.userRepository.getUser.return_value = user
    service = CurrentUserService(unitOfWorkFactory)

    result = await service.resolveCurrentUser("token-hash")

    assert result == user
    unitOfWork.sessionRepository.getValidSession.assert_awaited_once_with(
        "token-hash"
    )
    unitOfWork.userRepository.getUser.assert_awaited_once_with(
        sessionDto.user_id
    )


@pytest.mark.asyncio
async def test_resolveCurrentUser_raisesInvalidSessionWhenMissing(
    unitOfWorkFactory,
    unitOfWork,
):
    unitOfWork.sessionRepository.getValidSession.return_value = None
    service = CurrentUserService(unitOfWorkFactory)

    with pytest.raises(InvalidSessionException):
        await service.resolveCurrentUser("token-hash")


@pytest.mark.asyncio
async def test_resolveCurrentUser_raisesUserNotFound(
    unitOfWorkFactory,
    unitOfWork,
    sessionDto,
):
    unitOfWork.sessionRepository.getValidSession.return_value = sessionDto
    unitOfWork.userRepository.getUser.return_value = None
    service = CurrentUserService(unitOfWorkFactory)

    with pytest.raises(UserNotFoundException):
        await service.resolveCurrentUser("token-hash")
