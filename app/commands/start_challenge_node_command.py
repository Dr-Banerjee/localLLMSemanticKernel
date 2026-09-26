from uuid import UUID


class StartChallengeNodeCommand:
    def __init__(self, userId: UUID, nodeId: int, conversationId: int) -> None:
        self.userId = userId
        self.nodeId = nodeId
        self.conversationId = conversationId
