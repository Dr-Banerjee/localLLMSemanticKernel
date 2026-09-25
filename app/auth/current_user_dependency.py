from fastapi import HTTPException, status, Request

from auth.current_user_service import CurrentUserService
from auth.session_token_service import SessionTokenService
from config.settings import Settings
from exceptions.invalid_session_exception import InvalidSessionException
from exceptions.user_not_found_exception import UserNotFoundException
from models.user import User


class CurrentUserDependency:

    def __init__(
        self,
        currentUserService: CurrentUserService,
        sessionTokenService: SessionTokenService,
        settings: Settings,
    ) -> None:
        self.currentUserService = currentUserService
        self.sessionTokenService = sessionTokenService
        self.sessionCookieName = settings.sessionCookieName

    async def resolveCurrentUser(
        self,
        request: Request,
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

        try:
            return await self.currentUserService.resolveCurrentUser(
                tokenHash
            )
        except InvalidSessionException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session",
            )
        except UserNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
