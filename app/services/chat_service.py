from data_transfer_objects.response import ResponseToUserRequest
from kernel.kernel import createKernel
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.ollama import OllamaChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory
from models.conversation_course import ConversationCourse
from data_transfer_objects.request import UserRequest
from utils.load_prompt import LoadPrompt

class ChatService:
    #constructor
    def __init__(self):
        self.kernel = createKernel()
        self.chatService = self.kernel.get_service()
        self.settings = OllamaChatPromptExecutionSettings(
            temperature=0.7,
            top_p=0.8,
            num_predict=500,
            function_choice_behavior=FunctionChoiceBehavior.Auto(),
        )
        self.histories = {}    
    
    #given a conversationId and a UserRequest we process the userRequest
    async def processUserRequest(self, conversationId: int, request: UserRequest) -> ResponseToUserRequest:
        conversationCourse = self.getOrCreateConversationCourse(conversationId=conversationId)
        #the actual string that the user sends in as input.
        userInput = request.userInput        
        chatHistory= self.addUserInputToConversationCourse(conversationCourse,userInput)
        response = await self.chatService.get_chat_message_content(
                                                                    chat_history=chatHistory,
                                                                    kernel=self.kernel,
                                                                    settings=self.settings,
                                                                )
        chatHistory.add_assistant_message(str(response))

        return ResponseToUserRequest(response=str(response))

    #given a conversationId gets the chat history corressponding to it
    def getOrCreateConversationCourse(self, conversationId: int) -> ConversationCourse:        
        #denotes whether it is a new conversation.
        historyNewlyCreated = False
        if conversationId not in self.histories:
            newChatHistory = ChatHistory()
            historyNewlyCreated = True
            #load and feed a prompt determining the tone and persona of the app
            loadPrompt = LoadPrompt()            
            systemPrompt = loadPrompt.loadPrompt("system_prompts.txt")
            newChatHistory.add_system_message(systemPrompt)            
            self.histories[conversationId] = newChatHistory
        conversationCourse = ConversationCourse(
                                                            conversationId=conversationId,
                                                            chatHistory=self.histories[conversationId], 
                                                            newlyCreated=historyNewlyCreated
                                                            )
        return conversationCourse
    
    #Handle addition of user input to chat history
    def addUserInputToConversationCourse(self, conversationCourse: ConversationCourse, userInput: str)->ChatHistory:
        conversationCourse = conversationCourse.chatHistory
        isNewlyCreatedChatHistory = conversationCourse.newlyCreated
        #A prompt template to explain an idiom with the userInput being the initial idiom.
        if isNewlyCreatedChatHistory:
            self.handleInitialUserRequest(conversationCourse, userInput)
        else:
            conversationCourse.add_user_message(userInput)
        return conversationCourse
    
    #Handle the initial user request
    def handleInitialUserRequest(self,chatHistory: ChatHistory, userInput: str)-> None:
        #The initial request is always to explain the meaning of an idiom
        loadPrompt = LoadPrompt()           
        initalAnswerPrompt = loadPrompt.loadPrompt("answer_prompts.txt")
        initalAnswerPrompt = initalAnswerPrompt.replace('{{$user_input}}',userInput)
        chatHistory.add_user_message(initalAnswerPrompt)
    
