from uuid import UUID

from abstractions.i_challenge_repository import IChallengeRepository
from db.models.challenge_progress import ChallengeProgress as ChallengeProgressRecord
from models.challenge_progress import ChallengeProgress
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class ChallengeRepository(IChallengeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def getChallengeProgress(self, userId: UUID) -> ChallengeProgress | None:
        result = await self.session.execute(
            select(ChallengeProgressRecord).where(
                ChallengeProgressRecord.user_id == userId
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            return None

        return _toChallengeProgress(record)

    async def createChallengeProgress(
        self,
        userId: UUID,
        challengeStep: int,
    ) -> ChallengeProgress:
        record = ChallengeProgressRecord(
            user_id=userId,
            challenge_step=challengeStep,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return _toChallengeProgress(record)

    async def updateChallengeProgress(
        self,
        userId: UUID,
        challengeStep: int,
    ) -> ChallengeProgress | None:
        result = await self.session.execute(
            select(ChallengeProgressRecord).where(
                ChallengeProgressRecord.user_id == userId
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            return None

        record.challenge_step = challengeStep
        record.updated_at = func.now()
        await self.session.flush()
        await self.session.refresh(record)
        return _toChallengeProgress(record)


def _toChallengeProgress(record: ChallengeProgressRecord) -> ChallengeProgress:
    return ChallengeProgress(
        user_id=record.user_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
        challenge_step=record.challenge_step,
    )
