from uuid import UUID

from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from data_transfer_objects.conversation_message import ConversationMessage
from data_transfer_objects.visited_challenge_node import VisitedChallengeNode
from exceptions.challenge_node_not_found_exception import ChallengeNodeNotFoundException
from exceptions.conversation_not_found_exception import ConversationNotFoundException
from utils.challenge_idioms import load_challenge_idioms


class OpenVisitedChallengeNodeQueryHandler:
    def __init__(self, unitOfWorkFactory: IUnitOfWorkFactory) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory

    async def handleOpenVisitedChallengeNodeQuery(
        self,
        userId: UUID,
        nodeId: int,
    ) -> VisitedChallengeNode:
        idioms = load_challenge_idioms()
        entry = idioms.get(nodeId)
        if entry is None:
            raise ChallengeNodeNotFoundException("Challenge node not found")

        async with self.unitOfWorkFactory.create() as unitOfWork:
            repository = unitOfWork.conversationRepository
            conversationId = await self._findConversationId(
                repository,
                userId,
                entry["idiom"],
            )
            if conversationId is None:
                raise ConversationNotFoundException("Conversation not found")

            conversation = await repository.getConversation(conversationId, userId)
            if conversation is None:
                raise ConversationNotFoundException("Conversation not found")

            records = await repository.getMessages(conversation.id, userId)
            messages = [
                ConversationMessage(
                    id=record.id,
                    role=record.role,
                    content=record.content,
                    createdAt=record.created_at,
                )
                for record in records
            ]

        return VisitedChallengeNode(
            conversationId=conversation.id,
            messages=messages,
        )

    async def _findConversationId(self, repository, userId: UUID, idiom: str) -> int | None:
        page = 1
        pageSize = 100
        while True:
            summaries = await repository.getConversationSummaries(userId, page, pageSize)
            hasNextPage = len(summaries) > pageSize
            for summary in summaries[:pageSize]:
                if summary.initialMessage == idiom:
                    return summary.id
            if not hasNextPage:
                return None
            page += 1
