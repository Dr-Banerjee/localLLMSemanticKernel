from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from abstractions.i_session_repository import ISessionRepository
from db.models.session import Session as SessionRecord
from data_transfer_objects.session import Session


class SessionRepository(ISessionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def createSession(
        self,
        userId: UUID,
        tokenHash: str,
        expiresAt: datetime,
    ) -> Session:
        record = SessionRecord(
            user_id=userId,
            token_hash=tokenHash,
            expires_at=expiresAt,
        )

        self.session.add(record)

        await self.session.flush()
        await self.session.refresh(record)

        return Session(user_id=record.user_id)

    async def getValidSession(
        self,
        tokenHash: str,
    ) -> Session | None:
        now = datetime.now(timezone.utc)

        result = await self.session.execute(
            select(SessionRecord)
            .where(
                SessionRecord.token_hash == tokenHash,
                SessionRecord.expires_at > now,
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            return None

        return Session(user_id=record.user_id)
