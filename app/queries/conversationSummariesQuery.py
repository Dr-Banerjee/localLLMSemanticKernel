from uuid import UUID
class ConversationSummariesQuery:
    def __init__(self,
                 userId: UUID,
                 page: int,
                 pageSize: int,):
        self.userId = userId
        self.page = page
        self.pageSize = pageSize