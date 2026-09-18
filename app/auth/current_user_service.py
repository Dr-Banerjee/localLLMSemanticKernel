from fastapi import HTTPException, status

from db.models import User
from db.unit_of_work_factory import UnitOfWorkFactory

class CurrentUserService:

    def __init__(
        self,
        unitOfWorkFactory: UnitOfWorkFactory,
        tokenHash: str
    ) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory
        self.tokenHash = tokenHash

    async def resolveCurrentUser(
        self,
    ) -> User:        

        async with self.unitOfWorkFactory.create() as unitOfWork:

            session = await unitOfWork.sessionRepository.getValidSession(
                self.tokenHash
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