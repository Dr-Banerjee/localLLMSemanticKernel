from uuid import UUID

from abstractions.i_chat_completion import IChatCompletion
from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from data_transfer_objects.chat_turn import ChatTurn
from data_transfer_objects.request import UserRequest
from data_transfer_objects.response import ResponseToUserRequest
from exceptions.conversation_forbidden_exception import ConversationForbiddenException
from models.conversation_course import ConversationCourse
from utils.load_prompt import LoadPrompt
from utils.user_input_sanitizer import UserInputSanitizer


class ChatCommandHandler:
    def __init__(
        self,
        unitOfWorkFactory: IUnitOfWorkFactory,
        chatCompletion: IChatCompletion,
    ) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory
        self.chatCompletion = chatCompletion
        self.userInputSanitizer = UserInputSanitizer()
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
        self.fallbackExplanationDe = """Meaning:
Das konnte ich gerade nicht erklären.

Why does it mean that?
Lass uns diese Wörter noch einmal versuchen, oder such dir ein anderes Idiom aus.

Example:
Pip says, "Piece of cake means something is easy."

Remember:
Neugierige Fragen helfen dir trotzdem beim Lernen."""
        self.followUpFallbackDe = (
            "Lass uns bei diesem Idiom bleiben. Stell mir noch eine neugierige Frage dazu."
        )
        self.leakedInstructionMarkers = (
            "You are a kind, patient, and encouraging teacher",
            "getIdiomHint",
            "The next user message is the idiom",
            "Du bist eine freundliche, geduldige und ermutigende Lehrkraft",
            "Die nächste Nachricht des Kindes ist das Idiom",
        )

    async def handleChatCommand(
        self,
        conversationId: int,
        request: UserRequest,
        userId: UUID,
    ) -> ResponseToUserRequest:
        userInput = self.userInputSanitizer.sanitize(request.userInput)

        conversationCourse = await self.getOrCreateConversationCourse(
            conversationId=conversationId,
            userId=userId,
            language=request.language,
        )
        chatHistory = await self.addUserInputToConversationCourse(
            conversationCourse,
            userInput,
            request.language,
        )
        assistantResponse = await self.chatCompletion.complete(
            self.limitModelContext(chatHistory, conversationCourse.newlyCreated)
        )
        assistantResponse = self.removeStars(assistantResponse)
        assistantResponse = self.replyToStore(
            assistantResponse,
            conversationCourse.newlyCreated,
            request.language,
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

    def replyToStore(
        self,
        assistantResponse: str,
        newlyCreated: bool,
        language: str,
    ) -> str:
        if newlyCreated:
            if self.explanationIsComplete(assistantResponse) and self.replyIsSafeToShow(
                assistantResponse
            ):
                return assistantResponse
            return self.fallbackFor(language)

        if self.replyIsSafeToShow(assistantResponse):
            return assistantResponse
        return self.followUpFor(language)

    def fallbackFor(self, language: str) -> str:
        if language == "de":
            return self.fallbackExplanationDe
        return self.fallbackExplanation

    def followUpFor(self, language: str) -> str:
        if language == "de":
            return self.followUpFallbackDe
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
        language: str = "en",
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
            systemPrompt = LoadPrompt().loadPromptFor("system", language)
            chatHistory.append(ChatTurn(role="system", content=systemPrompt))

            async with self.unitOfWorkFactory.create() as unitOfWork:
                await unitOfWork.conversationRepository.addMessage(
                    conversationId=conversationId,
                    role="system",
                    content=systemPrompt,
                )
        else:
            await self.applyOperatingLanguage(
                chatHistory,
                conversationId,
                language,
            )

        return ConversationCourse(
            conversationId=conversationId,
            chatHistory=chatHistory,
            newlyCreated=historyNewlyCreated,
        )

    async def applyOperatingLanguage(
        self,
        chatHistory: list[ChatTurn],
        conversationId: int,
        language: str,
    ) -> None:
        systemPrompt = LoadPrompt().loadPromptFor("system", language)
        for index, turn in enumerate(chatHistory):
            if turn.role != "system":
                continue
            if turn.content == systemPrompt:
                return
            chatHistory[index] = ChatTurn(role="system", content=systemPrompt)
            async with self.unitOfWorkFactory.create() as unitOfWork:
                await unitOfWork.conversationRepository.updateSystemMessage(
                    conversationId,
                    systemPrompt,
                )
            return

    async def addUserInputToConversationCourse(
        self,
        conversationCourse: ConversationCourse,
        userInput: str,
        language: str = "en",
    ) -> list[ChatTurn]:
        isNewlyCreatedChatHistory = conversationCourse.newlyCreated
        conversationId = conversationCourse.conversationId
        chatHistoryOfConversation = list(conversationCourse.chatHistory)

        if isNewlyCreatedChatHistory:
            self.handleInitialUserRequest(
                chatHistoryOfConversation,
                userInput,
                language,
            )
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
        language: str = "en",
    ) -> None:
        formatPrompt = LoadPrompt().loadPromptFor("answer", language)
        chatHistory.append(ChatTurn(role="system", content=formatPrompt))
        chatHistory.append(ChatTurn(role="user", content=userInput))
