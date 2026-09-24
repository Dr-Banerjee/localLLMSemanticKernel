from data_transfer_objects.response import ResponseToUserRequest
from kernel.kernel import createKernel
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.ollama import OllamaChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory
from models.conversation_course import ConversationCourse
from data_transfer_objects.request import UserRequest
from utils.load_prompt import LoadPrompt
from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from exceptions.exceptions import ConversationForbidden
from uuid import UUID

class ChatService:
    #constructor
    def __init__(self, unitOfWorkFactory: IUnitOfWorkFactory) -> None:
        self.kernel = createKernel()
        self.chatService = self.kernel.get_service()
        self.settings = OllamaChatPromptExecutionSettings(
            temperature=0.7,
            top_p=0.8,
            num_predict=500,
            function_choice_behavior=FunctionChoiceBehavior.Auto(),
        )
        self.unitOfWorkFactory = unitOfWorkFactory
    
    #given a conversationId and a UserRequest we process the userRequest
    async def processUserRequest(self, conversationId: int, request: UserRequest, userId: UUID) -> ResponseToUserRequest:
        conversationCourse = await self.getOrCreateConversationCourse(conversationId=conversationId, userId = userId)
        #the actual string that the user sends in as input.
        userInput = request.userInput        
        chatHistory= await self.addUserInputToConversationCourse(conversationCourse,userInput)
        response = await self.chatService.get_chat_message_content(
                                                                    chat_history=chatHistory,
                                                                    kernel=self.kernel,
                                                                    settings=self.settings,
                                                                )
        assistantResponse = str(response)
        chatHistory.add_assistant_message(assistantResponse)

        async with self.unitOfWorkFactory.create() as unitOfWork:
            await unitOfWork.conversationRepository.addMessage(
                conversationId=conversationId,
                role="assistant",
                content=assistantResponse,
            )

        return ResponseToUserRequest(response=assistantResponse)

    #given a conversationId gets the chat history corressponding to it
    async def getOrCreateConversationCourse(self, conversationId: int, userId: UUID) -> ConversationCourse:        
        #denotes whether it is a new conversation.
        historyNewlyCreated = False

        async with self.unitOfWorkFactory.create() as unitOfWork:
            conversationRepository = unitOfWork.conversationRepository
            conversation = await conversationRepository.getConversation(conversationId, userId) 
            if conversation is None:                
                conversationExists = await conversationRepository.conversationExists(conversationId)
                if conversationExists:
                    raise ConversationForbidden(
                        "Conversation does not belong to the current user"
                    )
                await conversationRepository.createConversation(conversationId, userId)
                historyNewlyCreated = True
            messages = await conversationRepository.getMessages(conversationId, userId)    

        chatHistory = ChatHistory()
        # Loose strings need to be stored in an enum als it needs to be fixed in the db that no ther roles are allowed.
        for message in messages:
            if message.role == "system":
                chatHistory.add_system_message(message.content)
            elif message.role == "user":
                chatHistory.add_user_message(message.content)
            elif message.role == "assistant":
                chatHistory.add_assistant_message(message.content)

        if historyNewlyCreated:
            loadPrompt = LoadPrompt()
            systemPrompt = loadPrompt.loadPrompt("system_prompts.txt")
            chatHistory.add_system_message(systemPrompt)

            async with self.unitOfWorkFactory.create() as unitOfWork:
                await unitOfWork.conversationRepository.addMessage(
                    conversationId=conversationId,
                    role="system",
                    content=systemPrompt,
                )
        conversationCourse = ConversationCourse(
                                                            conversationId=conversationId,
                                                            chatHistory=chatHistory, 
                                                            newlyCreated=historyNewlyCreated
                                                            )
        return conversationCourse
    
    #Handle addition of user input to chat history
    async def addUserInputToConversationCourse(self, conversationCourse: ConversationCourse, userInput: str)->ChatHistory:
        isNewlyCreatedChatHistory = conversationCourse.newlyCreated
        conversationId = conversationCourse.conversationId
        chatHistoryOfConversation = conversationCourse.chatHistory                
        #A prompt template to explain an idiom with the userInput being the initial idiom.
        if isNewlyCreatedChatHistory:
            self.handleInitialUserRequest(chatHistoryOfConversation, userInput)
        else:
            chatHistoryOfConversation.add_user_message(userInput)
        async with self.unitOfWorkFactory.create() as unitOfWork:
                        await unitOfWork.conversationRepository.addMessage(
                            conversationId=conversationId,
                            role="user",
                            content=userInput,
                        )
        return chatHistoryOfConversation
    
    #Handle the initial user request
    def handleInitialUserRequest(self,chatHistory: ChatHistory, userInput: str)-> None:
        #The initial request is always to explain the meaning of an idiom
        loadPrompt = LoadPrompt()           
        initalAnswerPrompt = loadPrompt.loadPrompt("answer_prompts.txt")
        initalAnswerPrompt = initalAnswerPrompt.replace('{{$user_input}}',userInput)        
        chatHistory.add_user_message(initalAnswerPrompt)
    
