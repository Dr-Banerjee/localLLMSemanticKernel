from uuid import UUID


class UpdateChallengeProgressCommand:
    def __init__(self, userId: UUID, challengeStep: int) -> None:
        self.userId = userId
        self.challengeStep = challengeStep
