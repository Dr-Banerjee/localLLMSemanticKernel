from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import Database
from db.models.conversation import Conversation
from db.models.message import Message

class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def getConversation(self, conversationId : int) -> Conversation | None:
        result = await self.session.execute(
            select(Conversation).where(
                Conversation.id == conversationId
            )
        )
        return result.scalar_one_or_none()
        
    async def createConversation(self, conversationId : int) -> Conversation:
        conversation = Conversation(
                                        id = conversationId
                                    )
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation
        
    async def addMessage(
        self,
        conversationId: int,
        role: str,
        content: str,
    ) -> Message:
        
        message = Message(
            conversation_id=conversationId,
            role=role,
            content=content,
        )

        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def getMessages(
        self,
        conversationId: int,
    ) -> list[Message]:
        
        result = await self.session.execute(
            select(Message)
            .where(
                Message.conversation_id == conversationId
            )
            .order_by(Message.id)
        )

        return list(result.scalars().all())
    #Is there a better way to deal with it?
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