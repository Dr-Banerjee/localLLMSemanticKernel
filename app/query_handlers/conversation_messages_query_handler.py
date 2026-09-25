from uuid import UUID

from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from data_transfer_objects.conversation_message import ConversationMessage
from exceptions.conversation_not_found_exception import ConversationNotFoundException


class ConversationMessagesQueryHandler:
    def __init__(self, unitOfWorkFactory: IUnitOfWorkFactory) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory

    async def handleConversationMessagesQuery(
        self,
        conversationId: int,
        userId: UUID,
    ) -> list[ConversationMessage]:
        async with self.unitOfWorkFactory.create() as unitOfWork:
            conversation = await unitOfWork.conversationRepository.getConversation(
                conversationId,
                userId,
            )
            if conversation is None:
                raise ConversationNotFoundException("Conversation not found")
            messages = await unitOfWork.conversationRepository.getMessages(
                conversationId,
                userId,
            )
            return [
                ConversationMessage(
                    id=message.id,
                    role=message.role,
                    content=message.content,
                    createdAt=message.created_at,
                )
                for message in messages
            ]
