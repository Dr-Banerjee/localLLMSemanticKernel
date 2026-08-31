from data_transfer_objects.request import UserRequest
from data_transfer_objects.response import ResponseToUserRequest
from services.single_chat_service import SingleChatService
from services.chat_service import ChatService

class AnswerService:
    def __init__(self):
        self.chatService = ChatService()
        self.singleChatService = SingleChatService()

    #function to feed the user input to the singleChatService.
    async def processSingleRequest(self, request: UserRequest) -> ResponseToUserRequest:
        response = await self.singleChatService.generate_response(request)
        return response

    #function to feed conversationId and user request to the chatService
    async def chatProcess(self, conversationId: int, request: UserRequest) -> ResponseToUserRequest:
        response = await self.chatService.processUserRequest(conversationId,request)        
        return response
    