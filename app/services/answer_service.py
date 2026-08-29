from models.request import UserRequest
from models.response import ResponseToUserRequest
import services.single_chat_service as singleChatService

#function to feed the user input to the LLM service.
async def process(request: UserRequest) -> ResponseToUserRequest:
    #Feed the user input to the LLM service and return the generated response
    return await singleChatService.generate_response(request)
    