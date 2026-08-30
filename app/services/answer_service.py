from models.request import UserRequest
from models.response import ResponseToUserRequest
from services.single_chat_service import SingleChatService
from services.chat_service import ChatService

chatService = ChatService()
singleChatService = SingleChatService()
#function to feed the user input to the LLM service.
async def process(request: UserRequest) -> ResponseToUserRequest:
    #Feed the user input to the LLM service and return the generated response
    return await singleChatService.generate_response(request)
async def chatProcess(conversationId: int, request: UserRequest) -> str:    
    return await chatService.processUserRequest(conversationId,request)
    