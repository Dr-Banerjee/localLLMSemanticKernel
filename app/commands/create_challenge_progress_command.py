from uuid import UUID


class CreateChallengeProgressCommand:
    def __init__(self, userId: UUID, challengeStep: int) -> None:
        self.userId = userId
        self.challengeStep = challengeStep
