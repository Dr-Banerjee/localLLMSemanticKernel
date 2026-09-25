import logging
from datetime import datetime, timezone

from data_transfer_objects.chat_turn import ChatTurn
from utils.chat_history_logger import ChatHistoryLogger


def test_log_withoutConversationId(caplog):
    logger = logging.getLogger("chat-history-test")
    historyLogger = ChatHistoryLogger(logger)
    history = [
        ChatTurn(role="user", content="hi"),
        ChatTurn(role="assistant", content="hello"),
    ]

    with caplog.at_level(logging.INFO, logger="chat-history-test"):
        historyLogger.log(history)

    assert "Chat history (2 messages)" in caplog.text
    assert "role=user | content=hi" in caplog.text
    assert "role=assistant | content=hello" in caplog.text


def test_log_withConversationId(caplog):
    logger = logging.getLogger("chat-history-test-id")
    historyLogger = ChatHistoryLogger(logger)

    with caplog.at_level(logging.INFO, logger="chat-history-test-id"):
        historyLogger.log(
            [ChatTurn(role="system", content="sys")],
            conversation_id="42",
        )

    assert "[conversation_id=42]" in caplog.text
