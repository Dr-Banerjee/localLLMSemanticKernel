import os
class Settings:
    def __init__(self) -> None:
        self.databaseUrl = os.environ["DATABASE_URL"]
