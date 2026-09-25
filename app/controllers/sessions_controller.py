from fastapi import APIRouter, Depends, Response

from auth.anonymous_session_service import AnonymousSessionService
from auth.current_user_dependency import CurrentUserDependency
from config.settings import Settings
from models.user import User


class SessionsController:
    def __init__(
        self,
        anonymousSessionService: AnonymousSessionService,
        currentUserDependency: CurrentUserDependency,
        settings: Settings,
    ) -> None:
        self.anonymousSessionService = anonymousSessionService
        self.currentUserDependency = currentUserDependency
        self.settings = settings
        self.router = APIRouter(prefix="/api/sessions")
        self._registerRoutes()

    def _registerRoutes(self) -> None:
        @self.router.post("/session")
        async def createSession(response: Response):
            sessionToken = await self.anonymousSessionService.createSession()
            response.set_cookie(
                key=self.settings.sessionCookieName,
                value=sessionToken,
                httponly=True,
                secure=self.settings.sessionCookieSecure,
                samesite=self.settings.sessionCookieSameSite,
                path="/",
                max_age=self.settings.anonymousSessionLifetimeDays * 24 * 60 * 60,
            )
            return {"message": "Session created"}

        @self.router.get("/me")
        async def getCurrentUser(
            currentUser: User = Depends(
                self.currentUserDependency.resolveCurrentUser
            ),
        ):
            return {
                "id": str(currentUser.id),
            }
