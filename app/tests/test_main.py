import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mainModule(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:pass@localhost/db",
    )
    monkeypatch.delenv("APP_ENV", raising=False)

    with (
        patch("db.database.create_async_engine"),
        patch("db.database.async_sessionmaker", return_value=MagicMock()),
        patch(
            "kernel.semantic_kernel_chat_completion.createKernel",
            return_value=MagicMock(
                get_service=MagicMock(return_value=MagicMock())
            ),
        ),
        patch(
            "kernel.semantic_kernel_chat_completion.OllamaChatPromptExecutionSettings"
        ),
        patch(
            "kernel.semantic_kernel_chat_completion.FunctionChoiceBehavior"
        ),
    ):
        sys.modules.pop("main", None)
        module = importlib.import_module("main")
        yield module
        sys.modules.pop("main", None)


def test_main_includesConversationAndSessionRouters(mainModule):
    openApiPaths = set(mainModule.app.openapi()["paths"])

    assert "/api/conversations/{conversationId}/messages" in openApiPaths
    assert "/api/conversations/summaries" in openApiPaths
    assert "/api/sessions/session" in openApiPaths
    assert "/api/sessions/me" in openApiPaths
