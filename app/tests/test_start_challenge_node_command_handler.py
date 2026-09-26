import pytest

from command_handlers.start_challenge_node_command_handler import (
    StartChallengeNodeCommandHandler,
)
from exceptions.challenge_node_not_found_exception import ChallengeNodeNotFoundException
from utils.challenge_idioms import format_challenge_response, load_challenge_idioms


@pytest.mark.asyncio
async def test_handleStartChallengeNodeCommand_createsConversation(
    unitOfWorkFactory,
    unitOfWork,
    userId,
):
    handler = StartChallengeNodeCommandHandler(unitOfWorkFactory)

    result = await handler.handleStartChallengeNodeCommand(userId, 1)

    entry = load_challenge_idioms()[1]
    createCall = unitOfWork.conversationRepository.createConversation.await_args
    assert createCall.args[0] == result.conversation_id
    assert createCall.args[1] == userId
    messages = unitOfWork.conversationRepository.addMessage.await_args_list
    assert [call.args[1] for call in messages] == ["system", "user", "assistant"]
    assert messages[1].args[2] == entry["idiom"]
    assert messages[2].args[2] == format_challenge_response(entry)
    assert messages[0].args[2].strip() != ""


@pytest.mark.asyncio
async def test_handleStartChallengeNodeCommand_unknownNode(
    unitOfWorkFactory,
    userId,
):
    handler = StartChallengeNodeCommandHandler(unitOfWorkFactory)

    with pytest.raises(ChallengeNodeNotFoundException):
        await handler.handleStartChallengeNodeCommand(userId, 999999)
