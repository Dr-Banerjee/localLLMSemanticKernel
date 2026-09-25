from pathlib import Path

import pytest

from utils.load_prompt import LoadPrompt


def test_loadPrompt_readsExistingFile(tmp_path, monkeypatch):
    promptsDirectory = tmp_path / "prompts"
    promptsDirectory.mkdir()
    promptFile = promptsDirectory / "system_prompts.txt"
    promptFile.write_text("hello prompt", encoding="utf-8")

    loader = LoadPrompt()
    monkeypatch.setattr(loader, "promptsDirectory", promptsDirectory)

    assert loader.loadPrompt("system_prompts.txt") == "hello prompt"


def test_loadPrompt_raisesWhenMissing(tmp_path, monkeypatch):
    loader = LoadPrompt()
    monkeypatch.setattr(loader, "promptsDirectory", tmp_path / "missing")

    with pytest.raises(FileNotFoundError):
        loader.loadPrompt("absent.txt")


def test_promptsDirectory_pointsAtAppPrompts():
    loader = LoadPrompt()

    assert loader.promptsDirectory.name == "prompts"
    assert isinstance(loader.promptsDirectory, Path)
