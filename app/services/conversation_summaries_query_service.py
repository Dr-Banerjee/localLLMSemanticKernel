from uuid import UUID
from db.unit_of_work_factory import UnitOfWorkFactory
from data_transfer_objects.conversation_summary import ConversationSummary
from data_transfer_objects.conversation_summary_response import ConversationSummaryResponse
class ConversationSummariesQueryService:
    def __init__(self,
                 unitOfWorkFactory: UnitOfWorkFactory) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory

    async def getConversationSummaries(self,
                                       userId: UUID,
                                       page: int,
                                       pageSize: int) -> list[ConversationSummary]:
        async with self.unitOfWorkFactory.create() as unitOfWork:
            rows = await unitOfWork.conversationRepository.getConversationSummaries(
                userId,
                page,
                pageSize
            )
            hasNextPage = False
            if len(rows) > pageSize:
                hasNextPage = True
            
            conversationSummaries = [ConversationSummary(
                                                        id=row["id"],
                                                        createdAt=row["createdAt"],
                                                        updatedAt=row["updatedAt"],
                                                        initialMessage=row["initialMessage"],) for row in rows]
            conversationSummariesResponse = ConversationSummaryResponse(
                                                                        items=conversationSummaries,
                                                                        page=page,
                                                                        pageSize=pageSize,
                                                                        hasNextPage=hasNextPage
                                                                        )
            return conversationSummariesResponse