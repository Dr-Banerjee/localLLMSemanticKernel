from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import Database
from db.models.conversation import Conversation
from db.models.message import Message
from uuid import UUID
from data_transfer_objects.conversation_summary import ConversationSummary

class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def getConversation(self, 
                              conversationId : int,
                              userId: UUID) -> Conversation | None:
        result = await self.session.execute(
            select(Conversation).where(
                Conversation.id == conversationId,
                Conversation.user_id == userId
            )
        )
        return result.scalar_one_or_none()
        
    async def createConversation(self, 
                                 conversationId : int,
                                 userId: UUID) -> Conversation:
        conversation = Conversation(
                                        id = conversationId,
                                        user_id = userId
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
        userId: UUID
    ) -> list[Message]:
        
        result = await self.session.execute(
            select(Message)
            .join(
                Conversation,
                Message.conversation_id == Conversation.id
            )
            .where(
                Message.conversation_id == conversationId,
                Conversation.user_id == userId,
            )
            .order_by(Message.id)
        )

        return list(result.scalars().all())
    
    async def conversationExists(self, 
                                  conversationId : int
                                  ) -> bool:
            result = await self.session.execute(
                select(Conversation).where(
                    Conversation.id == conversationId
                )
            )
            return result.scalar_one_or_none() is not None

    async def getConversationSummaries(
    self,
    userId: UUID,
    page: int,
    pageSize: int,
    ):
        offset = (page - 1) * pageSize

        initialMessage = (
            select(Message.content)
            .where(
                Message.conversation_id == Conversation.id,
                Message.role == "user",
            )
            .order_by(Message.id)
            .limit(1)
            .scalar_subquery()
        )

        result = await self.session.execute(
            select(
                Conversation.id.label("id"),
                Conversation.created_at.label("createdAt"),
                Conversation.updated_at.label("updatedAt"),
                initialMessage.label("initialMessage"),
            )
            .where(Conversation.user_id == userId)
            .order_by(
                Conversation.updated_at.desc(),
                Conversation.id.desc(),
            )
            .offset(offset)
            .limit(pageSize)
        )

        return result.mappings().all()