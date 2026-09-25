from abc import ABC, abstractmethod

from data_transfer_objects.chat_turn import ChatTurn


class IChatCompletion(ABC):
    @abstractmethod
    async def complete(self, messages: list[ChatTurn]) -> str:
        pass
