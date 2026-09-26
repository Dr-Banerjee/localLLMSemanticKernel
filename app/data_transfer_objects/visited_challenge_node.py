from pydantic import BaseModel, ConfigDict

from data_transfer_objects.conversation_message import ConversationMessage


class VisitedChallengeNode(BaseModel):
    model_config = ConfigDict(frozen=True)

    conversationId: int
    messages: list[ConversationMessage]
