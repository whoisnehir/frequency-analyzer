"""Tests for the command-line entry point."""

from pathlib import Path

import pytest

from frequency_analyzer.__main__ import parse_args


def test_path_is_read_from_the_command_line():
    args = parse_args(["samples/tone_440hz.wav"])

    assert args.path == Path("samples/tone_440hz.wav")


def test_missing_path_prints_usage_and_exits_with_code_2(capsys):
    with pytest.raises(SystemExit) as exit_info:
        parse_args([])

    assert exit_info.value.code == 2
    assert "usage: python -m frequency_analyzer" in capsys.readouterr().err


def test_extra_argument_is_rejected(capsys):
    with pytest.raises(SystemExit) as exit_info:
        parse_args(["tone.wav", "mix.wav"])

    assert exit_info.value.code == 2
    assert "unrecognized arguments: mix.wav" in capsys.readouterr().err
