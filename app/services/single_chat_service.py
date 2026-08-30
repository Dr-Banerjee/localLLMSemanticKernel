from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.ollama import OllamaChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from models.request import UserRequest
from models.response import ResponseToUserRequest
import requests
from semantic_kernel.functions import KernelFunctionFromPrompt
from semantic_kernel.functions import KernelArguments
from kernel.kernel import createKernel
from utils.load_prompt import LoadPrompt

#Service class which enables us to send single requests to the LLM
class SingleChatService:
    #constructor
    def __init__(self):
        pass
    #returns a semantic kernel function taking into account system as well as answer prompts.
    def createAnswerFunction(self)-> KernelFunctionFromPrompt:
        loadPrompt = LoadPrompt()
        systemPrompt = loadPrompt.loadPrompt("system_prompts.txt")
        answerPrompt = loadPrompt.loadPrompt("answer_prompts.txt")
        #form a prompt  with sytem and answer prompts to be used in the kernel function    
        prompt = f"""
                    <message role="system">
                    {systemPrompt}
                    </message>

                    <message role="user">
                    {answerPrompt}
                    </message>
                """
        #settings for prompt execution which says how varied the output should be, how many of the top probable tokens to consider,
        #how many tokens to predict, and how to choose between multiple functions if applicable.
        settings = OllamaChatPromptExecutionSettings(
            temperature=0.7,
            top_p=0.8,
            num_predict=500,
            function_choice_behavior=FunctionChoiceBehavior.Auto(),
            )
        #the kernel function that is suppossed to be expose the prompt to the LLM 
        answerFunction = KernelFunctionFromPrompt(
            function_name="generate_answer",
            description="Explains an English idiom to a child",
            prompt=prompt,
            prompt_execution_settings=settings
        )
        return answerFunction
        
    async def generate_response(self,userRequest: UserRequest) -> ResponseToUserRequest:
        kernel = createKernel()
        userInput = userRequest.userInput
        answerFunction = self.createAnswerFunction()
        #the arguments replace the placeholders in the prompt with the actual user input. 
        arguments = KernelArguments(
            user_input=userInput,
            )
        #the kernel invokes the kernel function with the arguments replacing the placeholders and returns the response from the LLM.    
        response = await kernel.invoke(answerFunction, arguments=arguments)
        responseToUserRequest = self.parseResponseText(response.value[0].items[0].text)
        return responseToUserRequest

    #Intended to parse the incoming string and return ResponseToUserRequest object
    def parseResponseText(self,text: str) -> ResponseToUserRequest:
        textArray = text.split('\n\n')
        responseToUserRequest = ResponseToUserRequest(meaning=textArray[0],
                                                    reason=textArray[1],
                                                    example=textArray[2],
                                                    remember=textArray[3]                                                    
                                                    )
        return responseToUserRequest

