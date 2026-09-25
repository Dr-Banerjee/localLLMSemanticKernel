from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from exceptions.invalid_session_exception import InvalidSessionException
from exceptions.user_not_found_exception import UserNotFoundException
from models.user import User


class CurrentUserService:

    def __init__(
        self,
        unitOfWorkFactory: IUnitOfWorkFactory,
    ) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory

    async def resolveCurrentUser(
        self,
        tokenHash: str,
    ) -> User:
        async with self.unitOfWorkFactory.create() as unitOfWork:
            session = await unitOfWork.sessionRepository.getValidSession(
                tokenHash
            )

            if session is None:
                raise InvalidSessionException("Invalid or expired session")

            user = await unitOfWork.userRepository.getUser(
                session.user_id
            )

            if user is None:
                raise UserNotFoundException("User not found")

            return user
