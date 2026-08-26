from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.ollama import OllamaChatPromptExecutionSettings
from models.request import UserRequest
from models.response import ResponseToUserRequest
import requests
from semantic_kernel.functions import KernelFunctionFromPrompt
from semantic_kernel.functions import KernelArguments
from kernel.kernel import createKernel

#given the fileName it loads the prompt out of it
def loadPrompt(fileName : str)-> str:
    with open(
        f"prompts/{fileName}",
        "r",
        encoding="utf-8"
        ) as file:
        prompt = file.read()
    return prompt

#returns a semantic kernel function taking into account system as well as answer prompts.
def createAnswerFunction()-> KernelFunctionFromPrompt:
    with open("prompts/answer_prompts.txt","r",encoding="utf-8") as file:
        prompt = file.read()
        answerFunction = KernelFunctionFromPrompt(
            function_name="generate_answer",
            description="Explains an English idiom to a child",
            prompt=prompt,
        )
        return answerFunction
    
async def generate_response(user_input: str) -> str:
    kernel = createKernel()

    chat_service = kernel.get_service(type= ChatCompletionClientBase)

    systemPrompt = loadPrompt("system_prompts.txt")
    answerPrompt = loadPrompt("answer_prompts.txt")

    answerPrompt = answerPrompt.replace(
        "{{$user_input}}",
        user_input,
    )

    chatHistory = ChatHistory()
    chatHistory.add_system_message(systemPrompt)
    chatHistory.add_user_message(answerPrompt)
    
    settings = OllamaChatPromptExecutionSettings(
        temperature=0.7,
        top_p=0.8,
        num_predict=500,
    )

    response = await chat_service.get_chat_message_content(
        chat_history=chatHistory,
        kernel=kernel,
        settings=settings
    )

    return str(response)    
