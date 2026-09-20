import pytest
from pydantic import ValidationError
from probe import Recipe, reel_url, acquire, api_key
from unittest.mock import patch
from subprocess import CompletedProcess


def test_key_from_env_file(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    path = tmp_path / ".env"
    path.write_text("GEMINI_API_KEY=fake-test-key\n", encoding="utf-8")
    assert api_key(path) == "fake-test-key"
    monkeypatch.setenv("GEMINI_API_KEY", "environment-test-key")
    assert api_key(path) == "environment-test-key"


def test_missing_or_blank_key(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    path = tmp_path / ".env"
    assert api_key(path) == ""
    path.write_text('GEMINI_API_KEY="   "\n', encoding="utf-8")
    assert api_key(path) == ""


@pytest.mark.parametrize("url", ["http://instagram.com/reel/ABC/", "https://evil.com/reel/ABC/",
    "https://instagram.com.evil.com/reel/ABC/", "https://user@instagram.com/reel/ABC/",
    "https://instagram.com:8443/reel/ABC/", "https://instagram.com/p/ABC/"])
def test_invalid_sources(url):
    with pytest.raises(ValueError):
        reel_url(url)


def test_tracking_is_removed():
    assert reel_url("https://instagram.com/reel/ABC/?igsh=secret") == "https://www.instagram.com/reel/ABC/"


def test_missing_quantities_stay_null():
    recipe = Recipe.model_validate({"title": None, "ingredients": [
        {"name": "farinha", "quantity_text": None, "evidence": []}],
        "steps": [], "warnings": ["Quantidade ausente"], "language": "pt-BR"})
    assert recipe.ingredients[0].quantity_text is None


def test_incomplete_model_response_rejected():
    with pytest.raises(ValidationError):
        Recipe.model_validate({"title": "Bolo"})


def test_acquisition_failure_does_not_count_as_success(tmp_path):
    with patch("probe.subprocess.run", return_value=CompletedProcess([], 1, "", "login required")):
        with pytest.raises(RuntimeError):
            acquire("https://www.instagram.com/reel/ABC/", tmp_path)
    assert (tmp_path / "acquisition-error.txt").read_text() == "login required"
