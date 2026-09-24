from abstractions.i_chat_completion import IChatCompletion
from data_transfer_objects.chat_turn import ChatTurn
from data_transfer_objects.request import UserRequest
from data_transfer_objects.response import ResponseToUserRequest
from utils.load_prompt import LoadPrompt


class SingleChatService:
    def __init__(self, chatCompletion: IChatCompletion) -> None:
        self.chatCompletion = chatCompletion

    async def generate_response(
        self,
        userRequest: UserRequest,
    ) -> ResponseToUserRequest:
        loadPrompt = LoadPrompt()
        systemPrompt = loadPrompt.loadPrompt("system_prompts.txt")
        answerPrompt = loadPrompt.loadPrompt("answer_prompts.txt")
        answerPrompt = answerPrompt.replace(
            "{{$user_input}}",
            userRequest.userInput,
        )

        responseText = await self.chatCompletion.complete(
            [
                ChatTurn(role="system", content=systemPrompt),
                ChatTurn(role="user", content=answerPrompt),
            ]
        )
        return self.parseResponseText(responseText)

    def parseResponseText(self, text: str) -> ResponseToUserRequest:
        return ResponseToUserRequest(response=text)
