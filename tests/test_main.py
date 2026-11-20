"""Tests for the command-line entry point."""

import subprocess
import sys
from pathlib import Path

import pytest

from frequency_analyzer import __main__ as entry_point
from frequency_analyzer.__main__ import main, parse_args
from frequency_analyzer.audio import AudioFileError


def test_path_is_read_from_the_command_line():
    args = parse_args(["samples/tone_440hz.wav"])

    assert args.path == Path("samples/tone_440hz.wav")


def test_path_is_optional():
    args = parse_args([])

    assert args.path is None


def test_extra_argument_is_rejected(capsys):
    with pytest.raises(SystemExit) as exit_info:
        parse_args(["tone.wav", "mix.wav"])

    assert exit_info.value.code == 2
    assert "unrecognized arguments: mix.wav" in capsys.readouterr().err


class _FakeRoot:
    """Stands in for tk.Tk: remembers whether the window was kept open."""

    def __init__(self):
        self.looped = False
        self.destroyed = False

    def mainloop(self):
        self.looped = True

    def destroy(self):
        self.destroyed = True


class _FakeWindow:
    """Stands in for AnalyzerWindow: remembers the files it was asked to show."""

    def __init__(self, root):
        self.root = root
        self.shown = []

    def show_file(self, path):
        if path.name == "missing.wav":
            raise AudioFileError(f"{path} does not exist.")
        self.shown.append(path)


@pytest.fixture
def fake_windows(monkeypatch):
    """Replace the real window with fakes and return the fake windows."""
    windows = []

    def create_window(root):
        windows.append(_FakeWindow(root))
        return windows[-1]

    monkeypatch.setattr(entry_point.tk, "Tk", _FakeRoot)
    monkeypatch.setattr(entry_point, "AnalyzerWindow", create_window)
    return windows


def test_main_opens_the_window_with_the_given_file(fake_windows):
    main(["samples/tone_440hz.wav"])

    [window] = fake_windows
    assert window.shown == [Path("samples/tone_440hz.wav")]
    assert window.root.looped


def test_main_opens_an_empty_window_without_a_file(fake_windows):
    main([])

    [window] = fake_windows
    assert window.shown == []
    assert window.root.looped


def test_file_that_cannot_be_analyzed_is_reported_without_a_window(
    fake_windows, capsys
):
    with pytest.raises(SystemExit) as exit_info:
        main(["samples/missing.wav"])

    [window] = fake_windows
    path = Path("samples/missing.wav")
    assert exit_info.value.code == 1
    assert capsys.readouterr().err == (
        f"python -m frequency_analyzer: error: {path} does not exist.\n"
    )
    assert window.root.destroyed
    assert not window.root.looped


def test_running_the_package_reports_a_missing_file(tmp_path):
    path = tmp_path / "missing.wav"

    result = subprocess.run(
        [sys.executable, "-m", "frequency_analyzer", str(path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert result.stderr == (
        f"python -m frequency_analyzer: error: {path} does not exist.\n"
    )
