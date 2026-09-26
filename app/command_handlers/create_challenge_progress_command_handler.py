from uuid import UUID

from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from exceptions.challenge_progress_already_exists_exception import (
    ChallengeProgressAlreadyExistsException,
)
from models.challenge_progress import ChallengeProgress


class CreateChallengeProgressCommandHandler:
    def __init__(self, unitOfWorkFactory: IUnitOfWorkFactory) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory

    async def handleCreateChallengeProgressCommand(
        self,
        userId: UUID,
        challengeStep: int,
    ) -> ChallengeProgress:
        async with self.unitOfWorkFactory.create() as unitOfWork:
            existing = await unitOfWork.challengeRepository.getChallengeProgress(userId)
            if existing is not None:
                raise ChallengeProgressAlreadyExistsException(
                    "Challenge progress already exists"
                )
            return await unitOfWork.challengeRepository.createChallengeProgress(
                userId,
                challengeStep,
            )
