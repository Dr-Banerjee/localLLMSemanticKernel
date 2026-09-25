from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.ollama import OllamaChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory

from abstractions.i_chat_completion import IChatCompletion
from data_transfer_objects.chat_turn import ChatTurn
from kernel.kernel import createKernel


class SemanticKernelChatCompletion(IChatCompletion):
    def __init__(self) -> None:
        self.kernel = createKernel()
        self.chatService = self.kernel.get_service()
        self.settings = OllamaChatPromptExecutionSettings(
            temperature=0.7,
            top_p=0.8,
            num_predict=500,
            function_choice_behavior=FunctionChoiceBehavior.Auto(),
        )

    async def complete(self, messages: list[ChatTurn]) -> str:
        chatHistory = ChatHistory()
        for message in messages:
            if message.role == "system":
                chatHistory.add_system_message(message.content)
            elif message.role == "user":
                chatHistory.add_user_message(message.content)
            elif message.role == "assistant":
                chatHistory.add_assistant_message(message.content)

        response = await self.chatService.get_chat_message_content(
            chat_history=chatHistory,
            kernel=self.kernel,
            settings=self.settings,
        )
        return str(response)
