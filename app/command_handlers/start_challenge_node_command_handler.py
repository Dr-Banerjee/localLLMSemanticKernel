import time
from uuid import UUID

from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from data_transfer_objects.challenge_node_conversation import ChallengeNodeConversation
from exceptions.challenge_node_not_found_exception import ChallengeNodeNotFoundException
from utils.challenge_idioms import format_challenge_response, load_challenge_idioms
from utils.load_prompt import LoadPrompt


class StartChallengeNodeCommandHandler:
    def __init__(self, unitOfWorkFactory: IUnitOfWorkFactory) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory

    async def handleStartChallengeNodeCommand(
        self,
        userId: UUID,
        nodeId: int,
    ) -> ChallengeNodeConversation:
        idioms = load_challenge_idioms()
        entry = idioms.get(nodeId)
        if entry is None:
            raise ChallengeNodeNotFoundException("Challenge node not found")

        conversationId = time.time_ns() // 1_000_000
        systemPrompt = LoadPrompt().loadPrompt("system_prompts.txt")
        assistantMessage = format_challenge_response(entry)

        async with self.unitOfWorkFactory.create() as unitOfWork:
            repository = unitOfWork.conversationRepository
            await repository.createConversation(conversationId, userId)
            await repository.addMessage(conversationId, "system", systemPrompt)
            await repository.addMessage(conversationId, "user", entry["idiom"])
            await repository.addMessage(conversationId, "assistant", assistantMessage)

        return ChallengeNodeConversation(conversation_id=conversationId)
