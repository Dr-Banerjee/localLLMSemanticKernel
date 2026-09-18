from pydantic import BaseModel, ConfigDict
from data_transfer_objects.conversation_summary import ConversationSummary 


class ConversationSummaryResponse(BaseModel):    
    model_config = ConfigDict(frozen=True)
    #The conversation summaries
    items: list[ConversationSummary]
    #The immediate page that will contain the list of these summaries
    page: int
    #Number of entries per page
    pageSize: int
    #Whether there are more results that might be shown in the next page
    hasNextPage: bool