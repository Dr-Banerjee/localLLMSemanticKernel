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
    systemPrompt = loadPrompt("system_prompts.txt")
    answerPrompt = loadPrompt("answer_prompts.txt")    
    prompt = f"""
                <message role="system">
                {systemPrompt}
                </message>

                <message role="user">
                {answerPrompt}
                </message>
            """
    settings = OllamaChatPromptExecutionSettings(
        temperature=0.7,
        top_p=0.8,
        num_predict=500,
        function_choice_behavior=FunctionChoiceBehavior.Auto(),
        )
    answerFunction = KernelFunctionFromPrompt(
        function_name="generate_answer",
        description="Explains an English idiom to a child",
        prompt=prompt,
        prompt_execution_settings=settings
    )
    return answerFunction
    
async def generate_response(user_input: str) -> str:
    kernel = createKernel()

    answerFunction = createAnswerFunction()
    arguments = KernelArguments(
        user_input=user_input,
        )    
    response = await kernel.invoke(answerFunction, arguments=arguments)
    
    return str(response)    
