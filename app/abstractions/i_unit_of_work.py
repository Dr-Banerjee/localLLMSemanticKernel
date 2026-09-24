from abc import ABC, abstractmethod

from abstractions.i_conversation_repository import IConversationRepository
from abstractions.i_session_repository import ISessionRepository
from abstractions.i_user_repository import IUserRepository


class IUnitOfWork(ABC):
    conversationRepository: IConversationRepository
    userRepository: IUserRepository
    sessionRepository: ISessionRepository

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, traceback) -> None:
        pass
