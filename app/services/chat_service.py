from data_transfer_objects.response import ResponseToUserRequest
from data_transfer_objects.chat_turn import ChatTurn
from models.conversation_course import ConversationCourse
from data_transfer_objects.request import UserRequest
from utils.load_prompt import LoadPrompt
from abstractions.i_chat_completion import IChatCompletion
from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from exceptions.exceptions import ConversationForbidden
from uuid import UUID


class ChatService:
    def __init__(
        self,
        unitOfWorkFactory: IUnitOfWorkFactory,
        chatCompletion: IChatCompletion,
    ) -> None:
        self.unitOfWorkFactory = unitOfWorkFactory
        self.chatCompletion = chatCompletion

    async def processUserRequest(
        self,
        conversationId: int,
        request: UserRequest,
        userId: UUID,
    ) -> ResponseToUserRequest:
        conversationCourse = await self.getOrCreateConversationCourse(
            conversationId=conversationId,
            userId=userId,
        )
        userInput = request.userInput
        chatHistory = await self.addUserInputToConversationCourse(
            conversationCourse,
            userInput,
        )
        assistantResponse = await self.chatCompletion.complete(chatHistory)

        async with self.unitOfWorkFactory.create() as unitOfWork:
            await unitOfWork.conversationRepository.addMessage(
                conversationId=conversationId,
                role="assistant",
                content=assistantResponse,
            )

        return ResponseToUserRequest(response=assistantResponse)

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
                    raise ConversationForbidden(
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
        loadPrompt = LoadPrompt()
        initalAnswerPrompt = loadPrompt.loadPrompt("answer_prompts.txt")
        initalAnswerPrompt = initalAnswerPrompt.replace(
            "{{$user_input}}",
            userInput,
        )
        chatHistory.append(ChatTurn(role="user", content=initalAnswerPrompt))
