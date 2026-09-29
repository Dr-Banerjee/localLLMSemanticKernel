import pytest

from exceptions.invalid_user_input_exception import InvalidUserInputException
from utils.user_input_sanitizer import UserInputSanitizer


class TestUserInputSanitizer:
    def setup_method(self) -> None:
        self.sanitizer = UserInputSanitizer()

    def test_sanitize_trimsAndCollapsesWhitespace(self) -> None:
        assert self.sanitizer.sanitize("  piece   of   cake  ") == "piece of cake"

    def test_sanitize_keepsLettersDigitsAndAllowedPunctuation(self) -> None:
        assert (
            self.sanitizer.sanitize("Don't say it that way?")
            == "Don't say it that way?"
        )

    def test_sanitize_keepsGermanLetters(self) -> None:
        assert (
            self.sanitizer.sanitize("Gibt es eine ähnliche Redewendung?")
            == "Gibt es eine ähnliche Redewendung?"
        )

    def test_sanitize_normalizesToNfc(self) -> None:
        decomposed = "cafe\u0301"
        assert self.sanitizer.sanitize(decomposed) == "café"

    def test_sanitize_stripsControlCharactersAndCollapsesToSpaces(self) -> None:
        assert self.sanitizer.sanitize("hello\x00\nworld") == "hello world"

    def test_sanitize_stripsBidirectionalOverrides(self) -> None:
        assert self.sanitizer.sanitize("hello\u202eworld") == "helloworld"

    def test_sanitize_rejectsHtmlMarkup(self) -> None:
        with pytest.raises(InvalidUserInputException, match="userInput is invalid"):
            self.sanitizer.sanitize("<script>alert(1)</script>")

    def test_sanitize_rejectsSqlMetacharacters(self) -> None:
        with pytest.raises(InvalidUserInputException, match="userInput is invalid"):
            self.sanitizer.sanitize("'; DROP TABLE messages;--")

    def test_sanitize_rejectsEmptyAfterStripping(self) -> None:
        with pytest.raises(InvalidUserInputException, match="userInput is required"):
            self.sanitizer.sanitize("   \n\t  ")

    def test_sanitize_rejectsOversizedInput(self) -> None:
        self.sanitizer.maxLength = 5
        with pytest.raises(InvalidUserInputException, match="userInput is invalid"):
            self.sanitizer.sanitize("piece of cake")
