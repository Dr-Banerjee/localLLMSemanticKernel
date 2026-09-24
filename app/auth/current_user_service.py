from fastapi import HTTPException, status

from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from models.user import User

class CurrentUserService:

    def __init__(
        self,
        unitOfWorkFactory: IUnitOfWorkFactory,
    ) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory

    async def resolveCurrentUser(
        self,
        tokenHash: str
    ) -> User:        

        async with self.unitOfWorkFactory.create() as unitOfWork:

            session = await unitOfWork.sessionRepository.getValidSession(
                tokenHash
            )

            if session is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired session",
                )

            user = await unitOfWork.userRepository.getUser(
                session.user_id
            )

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )
            return user