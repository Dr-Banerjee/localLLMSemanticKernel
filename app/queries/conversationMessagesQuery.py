from uuid import UUID
class ConversationMessagesQuery:
    def __init__(self,
                 conversationId: int,
                 userId: UUID,):
        self.conversationId = conversationId
        self.userId = userId