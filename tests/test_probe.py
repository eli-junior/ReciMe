import pytest
from pydantic import ValidationError
from probe import Recipe, reel_url, acquire, api_key
from unittest.mock import patch
from subprocess import CompletedProcess
import json


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
    "https://instagram.com:8443/reel/ABC/", "https://instagram.com/stories/ABC/"])
def test_invalid_sources(url):
    with pytest.raises(ValueError):
        reel_url(url)


def test_tracking_is_removed():
    assert reel_url("https://instagram.com/reel/ABC/?igsh=secret") == "https://www.instagram.com/reel/ABC/"


def test_post_link_is_accepted():
    assert reel_url("https://www.instagram.com/p/DdC8Aw1RQU4/?igsh=secret") == "https://www.instagram.com/p/DdC8Aw1RQU4/"


def test_missing_quantities_stay_null():
    recipe = Recipe.model_validate({"title": None, "ingredients": [
        {"name": "farinha", "quantity_text": None, "evidence": []}],
        "steps": [], "warnings": ["Quantidade ausente"], "language": "pt-BR"})
    assert recipe.ingredients[0].quantity_text is None


def test_incomplete_model_response_rejected():
    with pytest.raises(ValidationError):
        Recipe.model_validate({"title": "Bolo"})


def test_acquisition_failure_does_not_count_as_success(tmp_path):
    with patch("probe.shutil.which", return_value="/usr/bin/ffprobe"), patch("probe.subprocess.run", return_value=CompletedProcess([], 1, "", "login required")):
        with pytest.raises(RuntimeError):
            acquire("https://www.instagram.com/reel/ABC/", tmp_path)
    assert (tmp_path / "acquisition-error.txt").read_text() == "login required"


@pytest.mark.parametrize("tracks,valid", [(["video", "audio"], True), (["video"], False), (["audio"], False), ([], False)])
def test_download_requires_audio_and_video(tmp_path, tracks, valid):
    (tmp_path / "video.mp4").write_bytes(b"test-media")
    (tmp_path / "video.info.json").write_text('{"description": "Legenda"}')
    inspection = json.dumps({"streams": [{"codec_type": track} for track in tracks]})
    with patch("probe.shutil.which", return_value="/usr/bin/ffprobe"), patch(
        "probe.subprocess.run", side_effect=[CompletedProcess([], 0, "", ""), CompletedProcess([], 0, inspection, "")]
    ):
        if valid:
            video, info = acquire("https://www.instagram.com/p/ABC/", tmp_path)
            assert video.is_file()
            assert info["description"] == "Legenda"
        else:
            with pytest.raises(RuntimeError, match="ambas as faixas"):
                acquire("https://www.instagram.com/p/ABC/", tmp_path)


def test_missing_ffprobe_stops_before_download(tmp_path):
    with patch("probe.shutil.which", return_value=None), patch("probe.subprocess.run") as run:
        with pytest.raises(RuntimeError, match="Instale FFmpeg"):
            acquire("https://www.instagram.com/p/ABC/", tmp_path)
        run.assert_not_called()
