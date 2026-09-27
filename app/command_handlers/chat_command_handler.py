from uuid import UUID

from abstractions.i_chat_completion import IChatCompletion
from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from data_transfer_objects.chat_turn import ChatTurn
from data_transfer_objects.request import UserRequest
from data_transfer_objects.response import ResponseToUserRequest
from exceptions.conversation_forbidden_exception import ConversationForbiddenException
from models.conversation_course import ConversationCourse
from utils.load_prompt import LoadPrompt


class ChatCommandHandler:
    def __init__(
        self,
        unitOfWorkFactory: IUnitOfWorkFactory,
        chatCompletion: IChatCompletion,
    ) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory
        self.chatCompletion = chatCompletion
        self.fallbackExplanation = """Meaning:
I couldn't explain that saying just now.

Why does it mean that?
Let's try those words again, or pick another idiom.

Example:
Pip says, "Piece of cake means something is easy."

Remember:
Curious questions still help you learn."""
        self.followUpFallback = (
            "Let's stay with this idiom. Ask me another curious question about it."
        )
        self.leakedInstructionMarkers = (
            "You are a kind, patient, and encouraging teacher",
            "getIdiomHint",
            "The next user message is the idiom",
        )

    async def handleChatCommand(
        self,
        conversationId: int,
        request: UserRequest,
        userId: UUID,
    ) -> ResponseToUserRequest:
        userInput = request.userInput.strip()
        if not userInput:
            raise ValueError("userInput is required")

        conversationCourse = await self.getOrCreateConversationCourse(
            conversationId=conversationId,
            userId=userId,
        )
        chatHistory = await self.addUserInputToConversationCourse(
            conversationCourse,
            userInput,
        )
        assistantResponse = await self.chatCompletion.complete(
            self.limitModelContext(chatHistory, conversationCourse.newlyCreated)
        )
        assistantResponse = self.removeStars(assistantResponse)
        assistantResponse = self.replyToStore(
            assistantResponse,
            conversationCourse.newlyCreated,
        )

        async with self.unitOfWorkFactory.create() as unitOfWork:
            await unitOfWork.conversationRepository.addMessage(
                conversationId=conversationId,
                role="assistant",
                content=assistantResponse,
            )

        return ResponseToUserRequest(response=assistantResponse)

    def removeStars(self, assistantResponse: str) -> str:
        return assistantResponse.replace("*", "")

    def replyToStore(self, assistantResponse: str, newlyCreated: bool) -> str:
        if newlyCreated:
            if self.explanationIsComplete(assistantResponse) and self.replyIsSafeToShow(
                assistantResponse
            ):
                return assistantResponse
            return self.fallbackExplanation

        if self.replyIsSafeToShow(assistantResponse):
            return assistantResponse
        return self.followUpFallback

    def explanationIsComplete(self, text: str) -> bool:
        normalized = text.replace("\r\n", "\n")
        return (
            "Meaning:" in normalized
            and "Why does it mean that?" in normalized
            and "Example:" in normalized
        )

    def replyIsSafeToShow(self, text: str) -> bool:
        stripped = text.strip()
        if not stripped:
            return False
        return not any(marker in stripped for marker in self.leakedInstructionMarkers)

    def limitModelContext(
        self,
        chatHistory: list[ChatTurn],
        newlyCreated: bool,
    ) -> list[ChatTurn]:
        if newlyCreated:
            return chatHistory

        systemTurns = [turn for turn in chatHistory if turn.role == "system"]
        userTurns = [turn for turn in chatHistory if turn.role == "user"]
        assistantTurns = [turn for turn in chatHistory if turn.role == "assistant"]

        context = list(systemTurns)
        if userTurns:
            context.append(userTurns[0])
        if assistantTurns:
            context.append(assistantTurns[-1])
        if len(userTurns) > 1:
            context.append(userTurns[-1])
        return context

    async def getOrCreateConversationCourse(
        self,
        conversationId: int,
        userId: UUID,
    ) -> ConversationCourse:
        historyNewlyCreated = False

        async with self.unitOfWorkFactory.create() as unitOfWork:
            conversationRepository = unitOfWork.conversationRepository
            conversation = await conversationRepository.getConversation(
                conversationId,
                userId,
            )
            if conversation is None:
                conversationExists = await conversationRepository.conversationExists(
                    conversationId
                )
                if conversationExists:
                    raise ConversationForbiddenException(
                        "Conversation does not belong to the current user"
                    )
                await conversationRepository.createConversation(
                    conversationId,
                    userId,
                )
                historyNewlyCreated = True
            messages = await conversationRepository.getMessages(
                conversationId,
                userId,
            )

        chatHistory = [
            ChatTurn(role=message.role, content=message.content)
            for message in messages
            if message.role in ("system", "user", "assistant")
        ]

        if historyNewlyCreated:
            loadPrompt = LoadPrompt()
            systemPrompt = loadPrompt.loadPrompt("system_prompts.txt")
            chatHistory.append(ChatTurn(role="system", content=systemPrompt))

            async with self.unitOfWorkFactory.create() as unitOfWork:
                await unitOfWork.conversationRepository.addMessage(
                    conversationId=conversationId,
                    role="system",
                    content=systemPrompt,
                )

        return ConversationCourse(
            conversationId=conversationId,
            chatHistory=chatHistory,
            newlyCreated=historyNewlyCreated,
        )

    async def addUserInputToConversationCourse(
        self,
        conversationCourse: ConversationCourse,
        userInput: str,
    ) -> list[ChatTurn]:
        isNewlyCreatedChatHistory = conversationCourse.newlyCreated
        conversationId = conversationCourse.conversationId
        chatHistoryOfConversation = list(conversationCourse.chatHistory)

        if isNewlyCreatedChatHistory:
            self.handleInitialUserRequest(chatHistoryOfConversation, userInput)
        else:
            chatHistoryOfConversation.append(
                ChatTurn(role="user", content=userInput)
            )

        async with self.unitOfWorkFactory.create() as unitOfWork:
            await unitOfWork.conversationRepository.addMessage(
                conversationId=conversationId,
                role="user",
                content=userInput,
            )
        return chatHistoryOfConversation

    def handleInitialUserRequest(
        self,
        chatHistory: list[ChatTurn],
        userInput: str,
    ) -> None:
        formatPrompt = LoadPrompt().loadPrompt("answer_prompts.txt")
        chatHistory.append(ChatTurn(role="system", content=formatPrompt))
        chatHistory.append(ChatTurn(role="user", content=userInput))
