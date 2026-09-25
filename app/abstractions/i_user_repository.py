from abc import ABC, abstractmethod
from uuid import UUID

from models.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def createUser(self) -> User:
        pass

    @abstractmethod
    async def getUser(self, userId: UUID) -> User | None:
        pass
