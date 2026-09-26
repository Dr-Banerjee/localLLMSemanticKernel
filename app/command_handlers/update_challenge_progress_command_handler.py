from uuid import UUID

from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from exceptions.challenge_progress_not_found_exception import (
    ChallengeProgressNotFoundException,
)
from models.challenge_progress import ChallengeProgress


class UpdateChallengeProgressCommandHandler:
    def __init__(self, unitOfWorkFactory: IUnitOfWorkFactory) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory

    async def handleUpdateChallengeProgressCommand(
        self,
        userId: UUID,
        challengeStep: int,
    ) -> ChallengeProgress:
        async with self.unitOfWorkFactory.create() as unitOfWork:
            updated = await unitOfWork.challengeRepository.updateChallengeProgress(
                userId,
                challengeStep,
            )
            if updated is None:
                raise ChallengeProgressNotFoundException("Challenge progress not found")
            return updated
