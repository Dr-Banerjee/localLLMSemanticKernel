from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from data_transfer_objects.session import Session


class ISessionRepository(ABC):
    @abstractmethod
    async def createSession(
        self,
        userId: UUID,
        tokenHash: str,
        expiresAt: datetime,
    ) -> Session:
        pass

    @abstractmethod
    async def getValidSession(self, tokenHash: str) -> Session | None:
        pass
