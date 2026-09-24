from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from abstractions.i_user_repository import IUserRepository
from db.models.user import User as UserRecord
from models.user import User


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def createUser(self) -> User:
        record = UserRecord()
        self.session.add(record)

        await self.session.flush()
        await self.session.refresh(record)

        return User(id=record.id)

    async def getUser(self, userId: UUID) -> User | None:
        result = await self.session.execute(
            select(UserRecord).where(
                UserRecord.id == userId
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            return None

        return User(id=record.id)
