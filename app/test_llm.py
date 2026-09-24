import asyncio
import sys

sys.path.insert(0, "app")

from data_transfer_objects.request import UserRequest
from kernel.semantic_kernel_chat_completion import SemanticKernelChatCompletion
from services.single_chat_service import SingleChatService


async def main():
    singleChatService = SingleChatService(SemanticKernelChatCompletion())
    newUserRequest = UserRequest(userInput="to perform a moonraker's errand")
    answer = await singleChatService.generate_response(newUserRequest)

    print(answer)


asyncio.run(main())
