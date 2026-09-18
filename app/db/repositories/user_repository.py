from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def createUser(self) -> User:
        user = User()
        self.session.add(user)

        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def getUser(self, userId: UUID) -> User:
        result = await self.session.execute(
            select(User).where(
                User.id == userId
            )
        )

        return result.scalar_one_or_none()