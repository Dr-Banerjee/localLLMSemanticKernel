from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.current_user_dependency import CurrentUserDependency
from commands.chat_command import ChatCommand
from data_transfer_objects.request import UserRequest
from exceptions.conversation_forbidden_exception import ConversationForbiddenException
from exceptions.conversation_not_found_exception import ConversationNotFoundException
from models.user import User
from queries.conversationMessagesQuery import ConversationMessagesQuery
from queries.conversationSummariesQuery import ConversationSummariesQuery
from utils.mediator import Mediator


class ConversationsController:
    def __init__(
        self,
        mediator: Mediator,
        currentUserDependency: CurrentUserDependency,
    ) -> None:
        self.mediator = mediator
        self.currentUserDependency = currentUserDependency
        self.router = APIRouter(prefix="/api/conversations")
        self._registerRoutes()

    def _registerRoutes(self) -> None:
        @self.router.post("/{conversationId}/messages")
        async def sendMessage(
            conversationId: int,
            request: UserRequest,
            currentUser: User = Depends(
                self.currentUserDependency.resolveCurrentUser
            ),
        ):
            try:
                return await self.mediator.send(
                    ChatCommand(
                        conversationId,
                        request,
                        currentUser.id,
                    )
                )
            except ConversationForbiddenException:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Conversation does not belong to the current user",
                )

        @self.router.get("/summaries")
        async def getConversationSummaries(
            currentUser: User = Depends(
                self.currentUserDependency.resolveCurrentUser
            ),
            page: int = Query(default=1, ge=1),
            pageSize: int = Query(default=20, ge=1, le=100),
        ):
            return await self.mediator.send(
                ConversationSummariesQuery(
                    userId=currentUser.id,
                    page=page,
                    pageSize=pageSize,
                )
            )

        @self.router.get("/{conversationId}/messages")
        async def getConversationMessages(
            conversationId: int,
            currentUser: User = Depends(
                self.currentUserDependency.resolveCurrentUser
            ),
        ):
            try:
                return await self.mediator.send(
                    ConversationMessagesQuery(
                        conversationId=conversationId,
                        userId=currentUser.id,
                    )
                )
            except ConversationNotFoundException:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found",
                )
