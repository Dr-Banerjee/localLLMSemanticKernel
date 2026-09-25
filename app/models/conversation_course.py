from pydantic import BaseModel

from data_transfer_objects.chat_turn import ChatTurn


class ConversationCourse(BaseModel):    
    conversationId: int
    chatHistory: list[ChatTurn]
    newlyCreated: bool
