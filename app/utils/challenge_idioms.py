import json
from pathlib import Path


def load_challenge_idioms() -> dict[int, dict[str, str]]:
    path = Path(__file__).resolve().parent / "challenge_idioms.json"
    with path.open(encoding="utf-8") as file:
        entries = json.load(file)
    return {int(entry["id"]): entry for entry in entries}


def format_challenge_response(entry: dict[str, str]) -> str:
    return (
        f"Meaning:\n{entry['meaning']}\n\n"
        f"Why does it mean that?\n{entry['nomenclature_reason']}\n\n"
        f"Example:\n{entry['example']}\n\n"
        f"Remember:\n{entry['remember']}"
    )
