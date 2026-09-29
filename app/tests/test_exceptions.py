from exceptions.conversation_forbidden_exception import ConversationForbiddenException
from exceptions.conversation_not_found_exception import ConversationNotFoundException
from exceptions.invalid_session_exception import InvalidSessionException
from exceptions.invalid_user_input_exception import InvalidUserInputException
from exceptions.user_not_found_exception import UserNotFoundException


def test_exception_types():
    assert issubclass(ConversationForbiddenException, Exception)
    assert issubclass(ConversationNotFoundException, Exception)
    assert issubclass(InvalidSessionException, Exception)
    assert issubclass(InvalidUserInputException, Exception)
    assert issubclass(UserNotFoundException, Exception)


def test_exceptions_carry_message():
    assert str(ConversationForbiddenException("x")) == "x"
    assert str(ConversationNotFoundException("y")) == "y"
    assert str(InvalidSessionException("z")) == "z"
    assert str(InvalidUserInputException("bad")) == "bad"
    assert str(UserNotFoundException("w")) == "w"
