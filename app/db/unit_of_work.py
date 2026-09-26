from sqlalchemy.ext.asyncio import AsyncSession

from abstractions.i_unit_of_work import IUnitOfWork
from db.database import Database
from db.repositories.challenge_repository import ChallengeRepository
from db.repositories.conversation_repository import ConversationRepository
from db.repositories.session_repository import SessionRepository
from db.repositories.user_repository import UserRepository


class UnitOfWork(IUnitOfWork):
    def __init__(self, database: Database):
        self.session: AsyncSession = database.createSession()
        self.conversationRepository = ConversationRepository(self.session)
        self.sessionRepository = SessionRepository(self.session)
        self.userRepository = UserRepository(self.session)
        self.challengeRepository = ChallengeRepository(self.session)      

    async def __aenter__(self) -> IUnitOfWork:        
        return self

    async def __aexit__(self, exc_type, exc_val, traceback) -> None:
        try:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()

