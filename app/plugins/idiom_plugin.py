from semantic_kernel.functions import kernel_function

class IdiomPlugin:
    def __init__(self):
        self.idioms = {
            "break the ice": {
                "meaning": (
                    "To do or say something that helps people feel "
                    "more comfortable when they first meet."
                ),
                "why": (
                    "Imagine a thick piece of ice between two people. "
                    "Breaking the ice means doing something that makes "
                    "the uncomfortable feeling disappear."
                ),
                "example": (
                    "Tom told a funny joke to break the ice when he "
                    "met his new classmates."
                ),
            },
            "piece of cake": {
                "meaning": (
                    "Something that is very easy to do."
                ),
                "why": (
                    "A piece of cake is usually easy and enjoyable to eat. "
                    "The expression compares something easy to a simple "
                    "and pleasant piece of cake."
                ),
                "example": (
                    "The homework was a piece of cake for Sarah."
                ),
            },
            "hit the books": {
                "meaning": (
                    "To start studying or working hard on schoolwork."
                ),
                "why": (
                    "The expression uses 'hit' in a playful way to mean "
                    "getting started with your books and studying seriously."
                ),
                "example": (
                    "I have a test tomorrow, so I need to hit the books tonight."
                ),
            },
            "to perform a moonraker's errand": {
                    "meaning": (
                    "To engage in an absurdly futile or foolish task based on a silly misunderstanding."
                    ),
                    "why": (
                    "Refers to an 18th-century Wiltshire legend where villagers tried to rake "
                    "the reflection of the full moon out of a pond, mistaking it for cheese."
                    ),
                    "example": (
                    "Sending the intern to buy a left-handed screwdriver was a total moonraker's errand."
                    ),
                },
        }

    @kernel_function(
        name="getIdiomHint",
        description=(
        "Gets reliable factual information about an English idiom. "
        "Returns the idiom's meaning, an explanation of why it has "
        "that meaning, and an example sentence. "
        "Use this function whenever you need factual information "
        "about an idiom instead of guessing."
    ),
    )

    def getIdiomHint(self, idiom: str) -> str:
        idiom = idiom.lower().strip()

        if idiom not in self.idioms:
            return f"I don't have information about the idiom '{idiom}'."

        idiom_data = self.idioms[idiom]

        return (
            f'Idiom: "{idiom}"\n'
            f"Meaning: {idiom_data['meaning']}\n"
            f"Why: {idiom_data['why']}\n"
            f"Example: {idiom_data['example']}"
        )