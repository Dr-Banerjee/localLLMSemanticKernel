import pytest

from config.settings import Settings


def test_settings_nonProductionDefaults(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("ANONYMOUS_SESSION_LIFETIME_DAYS", raising=False)
    monkeypatch.delenv("SESSION_COOKIE_NAME", raising=False)
    monkeypatch.delenv("SESSION_COOKIE_SECURE", raising=False)
    monkeypatch.delenv("SESSION_COOKIE_SAMESITE", raising=False)
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)

    settings = Settings()

    assert settings.databaseUrl.endswith("/db")
    assert settings.anonymousSessionLifetimeDays == 30
    assert settings.sessionCookieName == "session"
    assert settings.sessionCookieSecure is False
    assert settings.sessionCookieSameSite == "lax"
    assert "http://localhost:5173" in settings.corsAllowedOrigins


def test_settings_productionRequiresEnv(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ANONYMOUS_SESSION_LIFETIME_DAYS", "7")
    monkeypatch.setenv("SESSION_COOKIE_NAME", "host-session")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "true")
    monkeypatch.setenv("SESSION_COOKIE_SAMESITE", "strict")
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "https://a.example,https://b.example",
    )

    settings = Settings()

    assert settings.anonymousSessionLifetimeDays == 7
    assert settings.sessionCookieName == "host-session"
    assert settings.sessionCookieSecure is True
    assert settings.sessionCookieSameSite == "strict"
    assert settings.corsAllowedOrigins == [
        "https://a.example",
        "https://b.example",
    ]


def test_settings_requiresDatabaseUrl(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)

    with pytest.raises(KeyError):
        Settings()
