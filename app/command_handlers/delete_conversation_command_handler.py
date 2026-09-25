from uuid import UUID

from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from exceptions.conversation_not_found_exception import ConversationNotFoundException


class DeleteConversationCommandHandler:
    def __init__(self, unitOfWorkFactory: IUnitOfWorkFactory) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory

    async def handleDeleteConversationCommand(
        self,
        conversationId: int,
        userId: UUID,
    ) -> None:
        async with self.unitOfWorkFactory.create() as unitOfWork:
            conversation = await unitOfWork.conversationRepository.getConversation(
                conversationId,
                userId,
            )
            if conversation is None:
                raise ConversationNotFoundException("Conversation not found")
            await unitOfWork.conversationRepository.deleteConversation(
                conversationId,
                userId,
            )
