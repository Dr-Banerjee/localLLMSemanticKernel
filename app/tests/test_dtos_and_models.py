from datetime import datetime, timezone
from uuid import uuid7

from data_transfer_objects.chat_turn import ChatTurn
from data_transfer_objects.conversation import Conversation
from data_transfer_objects.conversation_message import ConversationMessage
from data_transfer_objects.conversation_summary import ConversationSummary
from data_transfer_objects.conversation_summary_response import (
    ConversationSummaryResponse,
)
from data_transfer_objects.message import Message
from data_transfer_objects.request import UserRequest
from data_transfer_objects.response import ResponseToUserRequest
from data_transfer_objects.session import Session
from models.conversation_course import ConversationCourse
from models.user import User


def test_userRequest_and_response_areFrozen():
    request = UserRequest(userInput="hi")
    response = ResponseToUserRequest(response="there")

    assert request.userInput == "hi"
    assert response.response == "there"


def test_chatTurn_and_message_models():
    now = datetime.now(timezone.utc)
    turn = ChatTurn(role="user", content="hi")
    message = Message(id=1, role="user", content="hi", created_at=now)

    assert turn.role == "user"
    assert message.created_at == now


def test_conversation_and_session_models():
    userId = uuid7()
    conversation = Conversation(id=3)
    session = Session(user_id=userId)

    assert conversation.id == 3
    assert session.user_id == userId


def test_conversationMessage_and_summary_models():
    now = datetime.now(timezone.utc)
    message = ConversationMessage(
        id=1,
        role="assistant",
        content="ok",
        createdAt=now,
    )
    summary = ConversationSummary(
        id=2,
        createdAt=now,
        updatedAt=now,
        initialMessage="start",
    )
    response = ConversationSummaryResponse(
        items=[summary],
        page=1,
        pageSize=20,
        hasNextPage=False,
    )

    assert message.createdAt == now
    assert response.items[0].id == 2


def test_user_and_conversationCourse():
    userId = uuid7()
    user = User(id=userId)
    course = ConversationCourse(
        conversationId=1,
        chatHistory=[ChatTurn(role="system", content="s")],
        newlyCreated=True,
    )

    assert user.id == userId
    assert course.newlyCreated is True
