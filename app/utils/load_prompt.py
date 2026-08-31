class LoadPrompt:
    def __init__(self):
        pass
    #given the fileName it loads the prompt out of it
    def loadPrompt(self,fileName : str)-> str:
        with open(
            f"prompts/{fileName}",
            "r",
            encoding="utf-8"
            ) as file:
            prompt = file.read()
        return prompt