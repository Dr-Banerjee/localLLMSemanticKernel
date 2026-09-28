from pathlib import Path
from typing import Literal

PromptKind = Literal["system", "answer"]
AppLanguage = Literal["en", "de"]

class LoadPrompt:
    promptFiles: dict[tuple[PromptKind, AppLanguage], str] = {
        ("system", "en"): "system_prompts.txt",
        ("system", "de"): "system_prompts_de.txt",
        ("answer", "en"): "answer_prompts.txt",
        ("answer", "de"): "answer_prompts_de.txt",
    }

    def __init__(self):
        self.promptsDirectory = (
            Path(__file__).resolve().parent.parent / "prompts"
        )

    def promptFileName(self, kind: PromptKind, language: str) -> str:
        if language not in ("en", "de"):
            raise ValueError("language must be en or de")
        selected: AppLanguage = "de" if language == "de" else "en"
        return self.promptFiles[(kind, selected)]

    def loadPromptFor(self, kind: PromptKind, language: str) -> str:
        return self.loadPrompt(self.promptFileName(kind, language))

    #given the fileName it loads the prompt out of it
    def loadPrompt(self,fileName : str)-> str:
        promptPath = self.promptsDirectory / fileName

        if not promptPath.is_file():
            raise FileNotFoundError(
                f"Prompt file not found: {promptPath}"
            )
        with open(
            promptPath,
            "r",
            encoding="utf-8"
            ) as file:
            prompt = file.read()
        return prompt