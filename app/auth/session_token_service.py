import hashlib
import secrets


class SessionTokenService:

    def generateToken(self) -> str:
        return secrets.token_urlsafe(32)

    def hashToken(self, token: str) -> str:
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()