import asyncio
from app.data_transfer_objects.request import UserRequest
from services.single_chat_service import SingleChatService

async def main():
    singleChatService = SingleChatService()
    newUserRequest = UserRequest(userInput="to perform a moonraker's errand")    
    answer = await singleChatService.generate_response(newUserRequest)

    print(answer)


asyncio.run(main())