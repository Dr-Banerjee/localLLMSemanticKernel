from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.session import Session


class SessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def createSession(
        self,
        userId: UUID,
        tokenHash: str,
        expiresAt: datetime,
    ) -> Session:
        session = Session(
            user_id=userId,
            token_hash=tokenHash,
            expires_at=expiresAt,
        )

        self.session.add(session)

        await self.session.flush()
        await self.session.refresh(session)

        return session

    async def getValidSession(
        self,
        tokenHash: str,
    ) -> Session | None:
        now = datetime.now(timezone.utc)

        result = await self.session.execute(
            select(Session)
            .where(
                Session.token_hash == tokenHash,
                Session.expires_at > now,
            )
        )

        return result.scalar_one_or_none()