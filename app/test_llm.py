import asyncio
import sys

sys.path.insert(0, "app")

from data_transfer_objects.chat_turn import ChatTurn
from data_transfer_objects.request import UserRequest
from kernel.semantic_kernel_chat_completion import SemanticKernelChatCompletion
from utils.load_prompt import LoadPrompt


async def main():
    chatCompletion = SemanticKernelChatCompletion()
    userRequest = UserRequest(userInput="to perform a moonraker's errand")
    loadPrompt = LoadPrompt()
    systemPrompt = loadPrompt.loadPrompt("system_prompts.txt")
    answerPrompt = loadPrompt.loadPrompt("answer_prompts.txt").replace(
        "{{$user_input}}",
        userRequest.userInput,
    )
    answer = await chatCompletion.complete(
        [
            ChatTurn(role="system", content=systemPrompt),
            ChatTurn(role="user", content=answerPrompt),
        ]
    )
    print(answer)


asyncio.run(main())
