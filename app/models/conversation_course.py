from semantic_kernel.contents import ChatHistory
from pydantic import BaseModel

class ConversationCourse(BaseModel):
    #Id of the conversation in question
    conversationId: int    
    #history of the chat corressponding to a conversationId
    chatHistory : ChatHistory
    #whether the chat history has been newly created. 
    #That is whether it  is a new conversation.
    newlyCreated: bool