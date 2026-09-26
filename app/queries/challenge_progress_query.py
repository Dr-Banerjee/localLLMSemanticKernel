from uuid import UUID


class ChallengeProgressQuery:
    def __init__(self, userId: UUID) -> None:
        self.userId = userId
