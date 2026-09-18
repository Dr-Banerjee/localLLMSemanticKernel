import os
class Settings:
    def __init__(self) -> None:
        self.databaseUrl = os.environ["DATABASE_URL"]
        self.anonymousSessionLifetimeDays = int(
            os.getenv(
                "ANONYMOUS_SESSION_LIFETIME_DAYS",
                "30"
            )
        )
