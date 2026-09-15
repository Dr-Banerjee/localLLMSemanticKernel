from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import Database
from db.models import Conversation
from db.models import Message

class ConversationRepository:
    def __init__(self, database : Database) -> None:
        self.database = database

    async def getConversation(self, conversationId : int) -> Conversation | None:
        async with self.database.createSession() as session:
            result = await session.execute(
                select(Conversation).where(
                    Conversation.id == conversationId
                )
            )
            return result.scalar_one_or_none()
        
    async def createConversation(self, conversationId : int) -> Conversation:
        async with self.database.createSession() as session:
            async with session.begin():
                conversation = Conversation(
                                                id = conversationId
                                            )
                session.add(conversation)
                await session.flush()
                await session.refresh(conversation)
            return conversation
        
    async def addMessage(
        self,
        conversationId: int,
        role: str,
        content: str,
    ) -> Message:
        async with self.database.createSession() as session:
            async with session.begin():
                message = Message(
                    conversation_id=conversationId,
                    role=role,
                    content=content,
                )

                session.add(message)
                await session.flush()
                await session.refresh(message)
            return message

    async def getMessages(
        self,
        conversationId: int,
    ) -> list[Message]:
        async with self.database.createSession() as session:
            result = await session.execute(
                select(Message)
                .where(
                    Message.id == conversationId
                )
                .order_by(Message.id)
            )

            return list(result.scalars().all())
    #Not pretty happy with creating sessions in this manner.
    async def getOrCreateConversation(
    self,
    conversationId: int,
    ) -> Conversation:
        conversation = await self.getConversation(
            conversationId
        )

        if conversation is not None:
            return conversation

        return await self.createConversation(
            conversationId
        )