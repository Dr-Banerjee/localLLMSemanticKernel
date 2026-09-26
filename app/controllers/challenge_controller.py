from fastapi import APIRouter, Depends, HTTPException, status

from auth.current_user_dependency import CurrentUserDependency
from commands.create_challenge_progress_command import CreateChallengeProgressCommand
from commands.start_challenge_node_command import StartChallengeNodeCommand
from commands.update_challenge_progress_command import UpdateChallengeProgressCommand
from data_transfer_objects.challenge_node_request import ChallengeNodeRequest
from data_transfer_objects.challenge_progress_request import ChallengeProgressRequest
from exceptions.challenge_node_not_found_exception import ChallengeNodeNotFoundException
from exceptions.challenge_progress_already_exists_exception import (
    ChallengeProgressAlreadyExistsException,
)
from exceptions.challenge_progress_not_found_exception import (
    ChallengeProgressNotFoundException,
)
from exceptions.conversation_not_found_exception import ConversationNotFoundException
from models.user import User
from queries.challenge_progress_query import ChallengeProgressQuery
from queries.open_visited_challenge_node_query import OpenVisitedChallengeNodeQuery
from utils.mediator import Mediator


class ChallengeController:
    def __init__(
        self,
        mediator: Mediator,
        currentUserDependency: CurrentUserDependency,
    ) -> None:
        self.mediator = mediator
        self.currentUserDependency = currentUserDependency
        self.router = APIRouter(prefix="/api/challenge")
        self._registerRoutes()

    def _registerRoutes(self) -> None:
        @self.router.post("/create")
        async def createChallengeProgress(
            request: ChallengeProgressRequest,
            currentUser: User = Depends(
                self.currentUserDependency.resolveCurrentUser
            ),
        ):
            try:
                return await self.mediator.send(
                    CreateChallengeProgressCommand(
                        userId=currentUser.id,
                        challengeStep=request.challenge_step,
                    )
                )
            except ChallengeProgressAlreadyExistsException:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Challenge progress already exists",
                )

        @self.router.patch("/update")
        async def updateChallengeProgress(
            request: ChallengeProgressRequest,
            currentUser: User = Depends(
                self.currentUserDependency.resolveCurrentUser
            ),
        ):
            try:
                return await self.mediator.send(
                    UpdateChallengeProgressCommand(
                        userId=currentUser.id,
                        challengeStep=request.challenge_step,
                    )
                )
            except ChallengeProgressNotFoundException:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Challenge progress not found",
                )

        @self.router.get("/get")
        async def getChallengeProgress(
            currentUser: User = Depends(
                self.currentUserDependency.resolveCurrentUser
            ),
        ):
            try:
                return await self.mediator.send(
                    ChallengeProgressQuery(userId=currentUser.id)
                )
            except ChallengeProgressNotFoundException:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Challenge progress not found",
                )

        @self.router.post("/node")
        async def startChallengeNode(
            request: ChallengeNodeRequest,
            currentUser: User = Depends(
                self.currentUserDependency.resolveCurrentUser
            ),
        ):
            try:
                return await self.mediator.send(
                    StartChallengeNodeCommand(
                        userId=currentUser.id,
                        nodeId=request.node_id,
                    )
                )
            except ChallengeNodeNotFoundException:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Challenge node not found",
                )

        @self.router.get("/visited/{nodeId}")
        async def openVisitedChallengeNode(
            nodeId: int,
            currentUser: User = Depends(
                self.currentUserDependency.resolveCurrentUser
            ),
        ):
            try:
                return await self.mediator.send(
                    OpenVisitedChallengeNodeQuery(
                        userId=currentUser.id,
                        nodeId=nodeId,
                    )
                )
            except ChallengeNodeNotFoundException:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Challenge node not found",
                )
            except ConversationNotFoundException:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found",
                )
