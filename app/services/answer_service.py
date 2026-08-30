from models.request import UserRequest
from models.response import ResponseToUserRequest
from services.single_chat_service import SingleChatService
from services.chat_service import ChatService

class AnswerService:
    def __init__(self):
        self.chatService = ChatService()
        self.singleChatService = SingleChatService()

    #function to feed the user input to the singleChatService.
    async def processSingleRequest(self, request: UserRequest) -> ResponseToUserRequest:
        #Feed the user input to the LLM service and return the generated response
        return await self.singleChatService.generate_response(request)

    #function to feed conversationId and user request to the chatService
    async def chatProcess(self, conversationId: int, request: UserRequest) -> str:    
        return await self.chatService.processUserRequest(conversationId,request)
    