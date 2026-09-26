from uuid import UUID


class OpenVisitedChallengeNodeQuery:
    def __init__(self, userId: UUID, nodeId: int) -> None:
        self.userId = userId
        self.nodeId = nodeId
