from datetime import datetime, timedelta, timezone
from auth.session_token_service import SessionTokenService
from config.settings import Settings
from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory

class AnonymousSessionService:
    def __init__(
            self,
            unitOfWorkFactory: IUnitOfWorkFactory,
            sessionTokenService: SessionTokenService,
            settings: Settings
    ) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory
        self.sessionTokenService = sessionTokenService
        self.settings = settings

    async def createSession(self) -> str:
        sessionToken = self.sessionTokenService.generateToken()
        tokenHash = self.sessionTokenService.hashToken(sessionToken)
        expiresAt = datetime.now(timezone.utc) + timedelta(days= self.settings.anonymousSessionLifetimeDays)

        async with self.unitOfWorkFactory.create() as unitOfWork:
            user = await unitOfWork.userRepository.createUser()
            await unitOfWork.sessionRepository.createSession(
                userId= user.id,
                tokenHash=tokenHash,
                expiresAt=expiresAt
            )
        return sessionToken