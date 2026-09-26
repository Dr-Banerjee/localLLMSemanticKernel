from uuid import UUID

from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from exceptions.challenge_progress_not_found_exception import (
    ChallengeProgressNotFoundException,
)
from models.challenge_progress import ChallengeProgress


class ChallengeProgressQueryHandler:
    def __init__(self, unitOfWorkFactory: IUnitOfWorkFactory) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory

    async def handleChallengeProgressQuery(self, userId: UUID) -> ChallengeProgress:
        async with self.unitOfWorkFactory.create() as unitOfWork:
            progress = await unitOfWork.challengeRepository.getChallengeProgress(userId)
            if progress is None:
                raise ChallengeProgressNotFoundException("Challenge progress not found")
            return progress
