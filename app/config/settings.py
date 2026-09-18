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

        self.sessionCookieName = os.getenv(
            "SESSION_COOKIE_NAME",
            "session",
        )

        self.sessionCookieSecure = os.getenv(
            "SESSION_COOKIE_SECURE",
            "false",
        ).lower() == "true"

        self.sessionCookieSameSite = os.getenv(
            "SESSION_COOKIE_SAMESITE",
            "lax",
        )

        self.corsAllowedOrigins = os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:4173,http://127.0.0.1:4173",
        ).split(",")
