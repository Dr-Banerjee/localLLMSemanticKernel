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


def test_promptFileName_selectsLanguage():
    loader = LoadPrompt()

    assert loader.promptFileName("system", "en") == "system_prompts.txt"
    assert loader.promptFileName("system", "de") == "system_prompts_de.txt"
    assert loader.promptFileName("answer", "en") == "answer_prompts.txt"
    assert loader.promptFileName("answer", "de") == "answer_prompts_de.txt"


def test_germanPrompts_keepEnglishIdiomsAndExamples():
    loader = LoadPrompt()
    systemPrompt = loader.loadPromptFor("system", "de")
    answerPrompt = loader.loadPromptFor("answer", "de")

    assert "auf Englisch bleiben" in systemPrompt
    assert "niemals deutsche" in systemPrompt
    assert "Meaning:" in answerPrompt
    assert "Example:" in answerPrompt
    assert "Tom told a funny joke to break the ice" in answerPrompt


def test_loadPromptFor_rejectsUnknownLanguage():
    with pytest.raises(ValueError, match="language must be en or de"):
        LoadPrompt().loadPromptFor("system", "fr")
