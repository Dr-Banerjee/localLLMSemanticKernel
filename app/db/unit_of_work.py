from sqlalchemy.ext.asyncio import AsyncSession
from db.database import Database
from db.repositories.conversation_repository import ConversationRepository

class UnitOfWork:
    def __init__(self, database: Database):
        self.session: AsyncSession = database.createSession()
        self.conversationRepository = ConversationRepository(self.session)

    async def __aenter__(self) -> UnitOfWork:        
        return self

    async def __aexit__(self, exc_type, exc_val, traceback) -> None:
        try:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()

