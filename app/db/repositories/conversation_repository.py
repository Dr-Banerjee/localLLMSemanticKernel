from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from abstractions.i_conversation_repository import IConversationRepository
from data_transfer_objects.conversation_summary import ConversationSummary
from db.models.conversation import Conversation as ConversationRecord
from db.models.message import Message as MessageRecord
from data_transfer_objects.conversation import Conversation
from data_transfer_objects.message import Message


class ConversationRepository(IConversationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def getConversation(
        self,
        conversationId: int,
        userId: UUID,
    ) -> Conversation | None:
        result = await self.session.execute(
            select(ConversationRecord).where(
                ConversationRecord.id == conversationId,
                ConversationRecord.user_id == userId,
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            return None

        return Conversation(id=record.id)

    async def createConversation(
        self,
        conversationId: int,
        userId: UUID,
    ) -> Conversation:
        record = ConversationRecord(
            id=conversationId,
            user_id=userId,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return Conversation(id=record.id)

    async def addMessage(
        self,
        conversationId: int,
        role: str,
        content: str,
    ) -> Message:
        record = MessageRecord(
            conversation_id=conversationId,
            role=role,
            content=content,
        )

        self.session.add(record)
        conversation = await self.session.get(
            ConversationRecord,
            conversationId,
        )
        conversation.updated_at = func.now()
        await self.session.flush()
        await self.session.refresh(record)
        return Message(
            id=record.id,
            role=record.role,
            content=record.content,
            created_at=record.created_at,
        )

    async def getMessages(
        self,
        conversationId: int,
        userId: UUID,
    ) -> list[Message]:
        result = await self.session.execute(
            select(MessageRecord)
            .join(
                ConversationRecord,
                MessageRecord.conversation_id == ConversationRecord.id,
            )
            .where(
                MessageRecord.conversation_id == conversationId,
                ConversationRecord.user_id == userId,
            )
            .order_by(MessageRecord.id)
        )

        return [
            Message(
                id=record.id,
                role=record.role,
                content=record.content,
                created_at=record.created_at,
            )
            for record in result.scalars().all()
        ]

    async def conversationExists(
        self,
        conversationId: int,
    ) -> bool:
        result = await self.session.execute(
            select(ConversationRecord).where(
                ConversationRecord.id == conversationId
            )
        )
        return result.scalar_one_or_none() is not None

    async def getConversationSummaries(
        self,
        userId: UUID,
        page: int,
        pageSize: int,
    ) -> list[ConversationSummary]:
        offset = (page - 1) * pageSize

        initialMessage = (
            select(MessageRecord.content)
            .where(
                MessageRecord.conversation_id == ConversationRecord.id,
                MessageRecord.role == "user",
            )
            .order_by(MessageRecord.id)
            .limit(1)
            .scalar_subquery()
        )

        result = await self.session.execute(
            select(
                ConversationRecord.id.label("id"),
                ConversationRecord.created_at.label("createdAt"),
                ConversationRecord.updated_at.label("updatedAt"),
                initialMessage.label("initialMessage"),
            )
            .where(
                ConversationRecord.user_id == userId,
                initialMessage.is_not(None),
            )
            .order_by(
                ConversationRecord.updated_at.desc(),
                ConversationRecord.id.desc(),
            )
            .offset(offset)
            .limit(pageSize + 1)
        )

        return [
            ConversationSummary(
                id=row["id"],
                createdAt=row["createdAt"],
                updatedAt=row["updatedAt"],
                initialMessage=row["initialMessage"],
            )
            for row in result.mappings().all()
        ]
