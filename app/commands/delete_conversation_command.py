from uuid import UUID


class DeleteConversationCommand:
    def __init__(
        self,
        conversationId: int,
        userId: UUID,
    ) -> None:
        self.conversationId = conversationId
        self.userId = userId
