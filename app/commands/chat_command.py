from uuid import UUID
from data_transfer_objects.request import UserRequest

class ChatCommand:
    def __init__(self, 
                 conversationId: int,
                request: UserRequest,
                userId: UUID,):
        self.conversationId = conversationId
        self.request = request
        self.userId = userId