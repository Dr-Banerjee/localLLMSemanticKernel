import logging
from semantic_kernel.contents import ChatHistory


class ChatHistoryLogger:
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger(__name__)

    def log(
        self,
        chat_history: ChatHistory,
        conversation_id: str | None = None,
    ) -> None:
        prefix = (
            f"[conversation_id={conversation_id}] "
            if conversation_id
            else ""
        )

        self.logger.info(
            "%sChat history (%d messages)",
            prefix,
            len(chat_history),
        )

        for index, message in enumerate(chat_history):
            self.logger.info(
                "%s[%d] role=%s | content=%s",
                prefix,
                index,
                message.role,
                message.content,
            )
