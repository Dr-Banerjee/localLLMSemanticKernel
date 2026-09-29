import unicodedata

from exceptions.invalid_user_input_exception import InvalidUserInputException


class UserInputSanitizer:
    maxLength = 500
    allowedPunctuation = {
        "'",
        "\u2018",
        "\u2019",
        '"',
        "\u00ab",
        "\u00bb",
        "\u201c",
        "\u201d",
        "\u201e",
        "?",
        "!",
        ".",
        ",",
        "-",
        "\u2013",
        "\u2014",
        "\u2026",
        "(",
        ")",
    }

    def sanitize(self, raw: str) -> str:
        normalized = unicodedata.normalize("NFC", raw)
        withoutControls = self.stripDisallowedControlCharacters(normalized)
        collapsed = " ".join(withoutControls.split())
        if not collapsed:
            raise InvalidUserInputException("userInput is required")
        if len(collapsed) > self.maxLength:
            raise InvalidUserInputException("userInput is invalid")
        if not self.containsOnlyAllowedCharacters(collapsed):
            raise InvalidUserInputException("userInput is invalid")
        return collapsed

    def stripDisallowedControlCharacters(self, text: str) -> str:
        cleanedCharacters = []
        for character in text:
            if character.isspace():
                cleanedCharacters.append(" ")
                continue
            category = unicodedata.category(character)
            if category.startswith("C"):
                continue
            cleanedCharacters.append(character)
        return "".join(cleanedCharacters)

    def containsOnlyAllowedCharacters(self, text: str) -> bool:
        for character in text:
            if character == " ":
                continue
            if character in self.allowedPunctuation:
                continue
            category = unicodedata.category(character)
            if (
                category.startswith("L")
                or category.startswith("N")
                or category.startswith("M")
            ):
                continue
            return False
        return True
