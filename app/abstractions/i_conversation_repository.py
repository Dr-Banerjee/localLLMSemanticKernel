from abc import ABC, abstractmethod
from uuid import UUID

from data_transfer_objects.conversation_summary import ConversationSummary
from data_transfer_objects.conversation import Conversation
from data_transfer_objects.message import Message


class IConversationRepository(ABC):
    @abstractmethod
    async def getConversation(
        self,
        conversationId: int,
        userId: UUID,
    ) -> Conversation | None:
        pass

    @abstractmethod
    async def createConversation(
        self,
        conversationId: int,
        userId: UUID,
    ) -> Conversation:
        pass

    @abstractmethod
    async def addMessage(
        self,
        conversationId: int,
        role: str,
        content: str,
    ) -> Message:
        pass

    @abstractmethod
    async def getMessages(
        self,
        conversationId: int,
        userId: UUID,
    ) -> list[Message]:
        pass

    @abstractmethod
    async def conversationExists(self, conversationId: int) -> bool:
        pass

    @abstractmethod
    async def getConversationSummaries(
        self,
        userId: UUID,
        page: int,
        pageSize: int,
    ) -> list[ConversationSummary]:
        pass

    @abstractmethod
    async def deleteConversation(
        self,
        conversationId: int,
        userId: UUID,
    ) -> None:
        pass
