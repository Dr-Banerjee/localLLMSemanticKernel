import asyncio
import os

from db.database import Database
from db.unit_of_work import UnitOfWork


async def main() -> None:
    database = Database(os.environ["DATABASE_URL"])

    conversationId = 987654

    try:
        async with UnitOfWork(database) as unitOfWork:
            conversation = (
                await unitOfWork.conversationRepository
                .getOrCreateConversation(conversationId)
            )

            print(
                "Conversation:",
                conversation.id,
            )

            message = (
                await unitOfWork.conversationRepository
                .addMessage(
                    conversationId=conversationId,
                    role="user",
                    content="Unit of Work test",
                )
            )

            print(
                "Message:",
                message.id,
                message.conversation_id,
            )

            messages = (
                await unitOfWork.conversationRepository
                .getMessages(conversationId)
            )

            print(
                "Messages in same unit of work:",
                len(messages),
            )

    finally:
        await database.dispose()


asyncio.run(main())