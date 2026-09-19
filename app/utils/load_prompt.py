from pathlib import Path

class LoadPrompt:
    def __init__(self):
        self.promptsDirectory = (
            Path(__file__).resolve().parent.parent / "prompts"
        )
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