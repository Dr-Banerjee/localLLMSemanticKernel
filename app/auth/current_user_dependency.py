from fastapi import Cookie, HTTPException, status, Request

from models.user import User
from auth.current_user_service import CurrentUserService
from auth.session_token_service import SessionTokenService
from config.settings import Settings

class CurrentUserDependency:

    SESSION_COOKIE_NAME = "session" #Need to configure it properly for prod it should be host session.

    def __init__(
        self,
        currentUserService: CurrentUserService,        
        sessionTokenService: SessionTokenService,
        settings: Settings
    ) -> None:
        self.currentUserService = currentUserService
        self.sessionTokenService = sessionTokenService
        self.sessionCookieName = settings.sessionCookieName

    async def resolveCurrentUser(
        self,
        request: Request
    ) -> User:
        sessionToken = request.cookies.get(
            self.sessionCookieName
        )        
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