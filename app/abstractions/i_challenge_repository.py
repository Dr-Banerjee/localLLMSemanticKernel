from abc import ABC, abstractmethod
from uuid import UUID

from models.challenge_progress import ChallengeProgress


class IChallengeRepository(ABC):
    @abstractmethod
    async def getChallengeProgress(self, userId: UUID) -> ChallengeProgress | None:
        pass

    @abstractmethod
    async def createChallengeProgress(
        self,
        userId: UUID,
        challengeStep: int,
    ) -> ChallengeProgress:
        pass

    @abstractmethod
    async def updateChallengeProgress(
        self,
        userId: UUID,
        challengeStep: int,
    ) -> ChallengeProgress | None:
        pass
