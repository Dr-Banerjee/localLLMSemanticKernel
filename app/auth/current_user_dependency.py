from fastapi import Cookie, HTTPException, status

from db.models.user import User
from auth.current_user_service import CurrentUserService
from auth.session_token_service import SessionTokenService

class CurrentUserDependency:

    SESSION_COOKIE_NAME = "session" #Need to configure it properly for prod it should be host session.

    def __init__(
        self,
        currentUserService: CurrentUserService,        
        sessionTokenService: SessionTokenService,
    ) -> None:
        self.currentUserService = currentUserService
        self.sessionTokenService = sessionTokenService

    async def resolveCurrentUser(
        self,
        sessionToken: str | None = Cookie(
            default=None,
            alias=SESSION_COOKIE_NAME,
        ),
    ) -> User:

        if sessionToken is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session required",
            )
        tokenHash = self.sessionTokenService.hashToken(
                    sessionToken
                )   

        return await self.currentUserService.resolveCurrentUser(
            tokenHash
        )