from uuid import UUID
from db.unit_of_work_factory import UnitOfWorkFactory
from data_transfer_objects.conversation_message import ConversationMessage
from fastapi import HTTPException, status

class ConversationMessagesQueryService:
    def __init__(self, unitOfWorkFactory: UnitOfWorkFactory) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory
    async def getConversationMessages(self, conversationId: int, userId: UUID) -> list[ConversationMessage]:
        # Logic to retrieve messages for the given conversationId and UserId
        async with self.unitOfWorkFactory.create() as unitOfWork:
                conversation = await unitOfWork.conversationRepository.getConversation(
                    conversationId,
                    userId,
                )
                if conversation is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Conversation not found",
                    )
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