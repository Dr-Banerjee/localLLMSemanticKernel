from uuid import UUID

from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from data_transfer_objects.conversation_summary_response import ConversationSummaryResponse


class ConversationSummariesQueryHandler:
    def __init__(self, unitOfWorkFactory: IUnitOfWorkFactory) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory

    async def handleConversationSummariesQuery(
        self,
        userId: UUID,
        page: int,
        pageSize: int,
    ) -> ConversationSummaryResponse:
        async with self.unitOfWorkFactory.create() as unitOfWork:
            summaries = await unitOfWork.conversationRepository.getConversationSummaries(
                userId,
                page,
                pageSize,
            )
            hasNextPage = len(summaries) > pageSize
            conversationSummaries = summaries[:pageSize]
            return ConversationSummaryResponse(
                items=conversationSummaries,
                page=page,
                pageSize=pageSize,
                hasNextPage=hasNextPage,
            )
